import sublime
import sublime_plugin
import threading
import shutil
import subprocess
import json, os, sys, time
from typing import List, Optional

PACKAGE = "Maven"
# --- Import helpers ---
pkg = os.path.join(sublime.packages_path(), PACKAGE, 'DockerHelper')
if pkg not in sys.path:
    sys.path.insert(0, pkg)
from DockerHelper import DockerHelper # now imports Packages/Maven/DockerHelper/DockerHelper.py

pkg = os.path.join(sublime.packages_path(), PACKAGE, 'ShellHelper')
if pkg not in sys.path:
    sys.path.insert(0, pkg)
from ShellHelper import ShellHelper # now imports Packages/Maven/ShellHelper/ShellHelper.py

pkg = os.path.join(sublime.packages_path(), PACKAGE, 'MavenHelper')
if pkg not in sys.path:
    sys.path.insert(0, pkg)
from MavenHelper import MavenHelper # now imports Packages/Maven/MavenHelper/MavenHelper.py


# --- End Import helpers ---

# --- Configuration ---
MENU_PATH = os.path.join(sublime.packages_path(), PACKAGE, "Side Bar.sublime-menu")
# Name used in the sidebar context menu
MAVEN_MENU_LABEL = PACKAGE
# If True, will add a disabled menu entry when docker not found.
SHOW_DISABLED_WHEN_NOT_FOUND = False

SETTINGS_FILE = PACKAGE.lower()+".sublime-settings"
# Default settings
CONTAINER_MODE=False
DOCKER_CONTAINER=None

dockerHelper = None
shellHelper = None
mavenHelper = None
mavenMenuPlaceholder = False
# --- End config ---

class Command:
    def __init__(self, title, type=None, flags=[False]):
        self.title = title
        self.type = type
        self.flags = flags

class Menu:
    def __init__(self, prefix, command,args):
        self.prefix = prefix
        self.command = command
        self.args = args
        self.children = []

    def add_child(self, command):
        self.children.append(command)

    @staticmethod
    def getFlags(main_commands, prefix, item_id):
        title = item_id.replace(f"{prefix}_", "").replace("_id", "")
        for command in main_commands:
            if Menu.normalizeStr(command.title) == title:
                return command.flags
            if isinstance(command.type, list):
                for sub_command in command.type:
                    if Menu.normalizeStr(sub_command.title) == title:
                        return sub_command.flags
        return None

    @staticmethod
    def normalizeStr(title):
        return title.replace(" ", "_").lower()

    def generate_menu(self, mainCommands):
        self.children = []
        for command in mainCommands:
            self.add_child(self.create_menu_item(command))
        return self.children

    def create_menu_item(self, command):
        item_id = f"{self.prefix}_{Menu.normalizeStr(command.title)}_id"
        item = {
            "caption": command.title,
            "id": item_id,
            "command": self.command,
            "args": {**self.args, "item_id": item_id}
        }
        if isinstance(command.type, list):
            item["children"] = []
            for sub_command in command.type:
                item["children"].append(self.create_menu_item(sub_command))
        return item

    def write_menu(self,mainCommands):
        menu = [
            {
                "id": f"{self.prefix}_group_id",
                "command": f"{self.prefix}_menu_placeholder",
                "args": {**self.args, "item_id":f"{self.prefix}_group_id"},
                "children": self.generate_menu(mainCommands)
            }
        ]
        os.makedirs(os.path.dirname(MENU_PATH), exist_ok=True)
        with open(MENU_PATH, "w", encoding="utf-8") as f:
            json.dump(menu, f, indent=2, ensure_ascii=False)


create_commands = [
    Command("Maven Archetype Quickstart", None, [False]),
]

main_commands = [
    Command("Create", create_commands, [False]),
    Command("Run", None, [True]),
    Command("Build", None, [True]),
    Command("Tests", None, [True]),
    Command("Clean", None, [True])
]
# Run initial check in background so startup isn't blocked
def plugin_loaded():
    global mavenMenuPlaceholder
    global dockerHelper
    global shellHelper
    global mavenHelper
    global PACKAGE
    global CONTAINER_MODE
    global DOCKER_CONTAINER
    global MAVEN_MENU_LABEL
    maven_menu_placeholder = "maven_menu_placeholder"

    def log(msg):
        global PACKAGE 
        print("["+PACKAGE+"]", msg)


    s = sublime.load_settings(SETTINGS_FILE)
    CONTAINER_MODE = s.get("container_mode", False)
    log("load settings: " + str(s.to_dict()))

    if CONTAINER_MODE == True:
        DOCKER_CONTAINER = s.get("docker_container", None)
        MAVEN_MENU_LABEL = MAVEN_MENU_LABEL + ":Container"
        dockerHelper = DockerHelper(DOCKER_CONTAINER)
        mavenHelper = MavenHelper(dockerHelper.runContainerCommand)
    else :
        shellHelper = ShellHelper()
        mavenHelper = MavenHelper(shellHelper.runHostCommand)

    if mavenHelper.isMavenAvailable() == True:
        mavenMenuPlaceholder = True
        menuInstance = Menu(PACKAGE.lower(),maven_menu_placeholder,{"paths": ["$folder"]})
        menuInstance.write_menu(main_commands)
    else:
        mavenMenuPlaceholder = False
    log("isMavenAvailable: " + str(mavenMenuPlaceholder))


class MavenMenuPlaceholderCommand(sublime_plugin.WindowCommand):
    global PACKAGE
    prefix = PACKAGE
    def log(self,msg):
        print("["+self.prefix+"]", msg)

    def getSelectedPath(self, paths: List[str]) -> Optional[str]:
        selectedFolder = None
        # Expect 'paths' from Side Bar menu args (["$file"] or ["$folder"])
        if not paths:
            # fallback to active file
            view = self.window.active_view()
            if view and view.file_name():
                paths = [view.file_name()]
            else:
                return None

        # Accept a list; take first item
        path = paths[0]
        if isinstance(path, dict) and "path" in path:
            path = path["path"]
        if not path:
            return None

        if os.path.isdir(path):
            selectedFolder = path
        elif os.path.isfile(path):
            selectedFolder = os.path.dirname(path)
        else:
            return None

        return selectedFolder

    def getSidebarPath(self) -> Optional[str]:
        # Find which top-level folder contains the path
        folders = self.window.folders()
        top = folders[0] if folders else None

        return top

    def getRelativePath(self, selectedFolderPath: str, windowFolderPath: str) -> Optional[str]:
        common = None
        try:
            common = os.path.commonpath([selectedFolderPath,windowFolderPath])
        except Exception:
            common = None

        if not common:
            return None

        # Compute relative path from top folder. If same folder, return "."
        rel = os.path.relpath(selectedFolderPath, common)
        if rel == ".":
            rel = "" # or keep "." depending on preference
        return rel

    def run(self, paths=None,item_id=None, returnPathType=0) -> Optional[str]:
        requestedPath = "No path was found!"
        if returnPathType == 0:
            return None
        elif returnPathType == 1:
            selectedFolder = self.getSelectedPath(paths)
            if selectedFolder != None:
                requestedPath = selectedFolder
        elif returnPathType == 2:
            windowFolder = self.getSidebarPath()
            if windowFolder != None:
                requestedPath = windowFolder
        elif returnPathType == 3:
            selectedFolder = self.getSelectedPath(paths)
            windowFolder = self.getSidebarPath()
            relativePath = self.getRelativePath(selectedFolder,windowFolder)
            if relativePath != None:
                requestedPath = relativePath 

        # Show result: Show status/quick panel
        sublime.status_message("Requested path: " + requestedPath)
        self.window.show_quick_panel([requestedPath], None)
        return requestedPath

    def is_enabled(self, paths=None, item_id=None, **kwargs):
        global mavenMenuPlaceholder
        return mavenMenuPlaceholder

    def is_visible(self, paths=None, item_id=None, **kwargs):
        # Always visible so the menu header shows even when disabled
        if item_id != None:
            selectedFolder = self.getSelectedPath(paths)
            windowFolder = self.getSidebarPath()
            if mavenHelper.isMavenProject(selectedFolder,windowFolder) == None:
                return not Menu.getFlags(main_commands ,self.prefix.lower(),item_id)[0]
            return Menu.getFlags(main_commands ,self.prefix.lower(),item_id)[0]
        return True

    def description(self, paths=None, item_id=None, **kwargs):
        global mavenHelper
        selectedFolder = self.getSelectedPath(paths)
        windowFolder = self.getSidebarPath()
        #self.log(item_id + " ,"+str(Menu.get_flag(main_commands ,item_id)))
        if item_id == "maven_group_id":
            requestedPath=""
            theReturnPath = mavenHelper.isMavenProject(selectedFolder,windowFolder)
            if theReturnPath != None:
                requestedPath=" ("+os.path.basename(theReturnPath)+")"

            return MAVEN_MENU_LABEL+requestedPath

