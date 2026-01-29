import sublime
import sublime_plugin
import json, os, sys, time
from typing import List, Optional

PACKAGE = "AddREADME"
# --- End Import helpers ---

# --- Configuration ---
MENU_PATH = os.path.join(sublime.packages_path(), PACKAGE, "Side Bar.sublime-menu")
TEMPLATES_PATH = os.path.join(sublime.packages_path(), PACKAGE, "templates")
# Name used in the sidebar context menu
#MAIN_MENU_LABEL = PACKAGE
MAIN_MENU_LABEL = "Add README"
# If True, will add a disabled menu entry when docker not found.
SHOW_DISABLED_WHEN_NOT_FOUND = False

SETTINGS_FILE = PACKAGE.lower()+".sublime-settings"

class Command:
    def __init__(self, title, type=None, flags=[False]):
        self.title = title
        self.type = type
        self.flags = flags

class Menu:
    global TEMPLATES_PATH

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

    def list_files(self, folderPath):
        files = []
        if os.path.isdir(folderPath):
            for name in sorted(os.listdir(folderPath)):
                if name.lower().endswith(".md"):
                    files.append(name)
        return files

    def generate_menu(self):
        children = []
        files = self.list_files(TEMPLATES_PATH)
        for label in files:
            item = {"caption": label, 
                "id": f"{self.prefix}_item_{label}",
                "command": f"{self.prefix}_menu_placeholder", 
                "args": {
                    "paths": ["$folder"],
                    "item_id": f"{self.prefix}_item_{label}",
                    "file": label,
                    "templatespath": TEMPLATES_PATH
                    }
                }
            item["caption"] = label
            children.append(item)
        return children

    def write_menu(self):
        menu = [
            {
                "id": f"{self.prefix}_group_id",
                "command": f"{self.prefix}_menu_placeholder",
                "args": {**self.args, "item_id":f"{self.prefix}_group_id"},
                "children": self.generate_menu()
            }
        ]
        os.makedirs(os.path.dirname(MENU_PATH), exist_ok=True)
        with open(MENU_PATH, "w", encoding="utf-8") as f:
            json.dump(menu, f, indent=2, ensure_ascii=False)

# Run initial check in background so startup isn't blocked
def plugin_loaded():
    global MAIN_MENU_LABEL
    global PACKAGE
    prefix = PACKAGE.lower()
    main_menu_placeholder = f"{prefix}_menu_placeholder"

    def log(msg):
        global PACKAGE 
        print("["+PACKAGE+"]", msg)

    menuInstance = Menu(prefix,main_menu_placeholder,{"paths": ["$folder"]})
    menuInstance.write_menu()
    log(str(main_menu_placeholder))

class AddreadmeMenuPlaceholderCommand(sublime_plugin.WindowCommand):
    global PACKAGE
    prefix = PACKAGE.lower()
    def log(self,msg):
        print("["+self.PACKAGE+"]", msg)

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

    def hasREADME(self,paths):
        selectedFolder = self.getSelectedPath(paths)
        windowFolder = self.getSidebarPath()
        if selectedFolder:
            readme_path = os.path.join(selectedFolder, "README.md")
            return os.path.exists(readme_path)
        return False

    def isMainMenuItemId(self, item_id):
        if item_id.startswith(f"{self.prefix}_item_"):
            return True
        return False

    def run(self, paths=None,item_id=None, **kwargs) -> Optional[str]:
        if item_id != None and self.isMainMenuItemId(item_id) == True:
            if 'file' in kwargs and 'templatespath' in kwargs:
                selectedFolder = self.getSelectedPath(paths)
                full_template_path = os.path.join(kwargs['templatespath'], kwargs['file'])
                full_readme_path = os.path.join(selectedFolder, "README.md")
                if not os.path.exists(full_readme_path):
                    # Check if the template file exists
                    if not os.path.exists(full_template_path):
                        sublime.message_dialog(f"Template file not found: {full_template_path}")
                        return

                    # Create README.md from the template
                    with open(full_template_path, 'r') as template_file:
                        content = template_file.read()

                    with open(full_readme_path, 'w') as readme_file:
                        readme_file.write(content)

                    # Open the created README.md file
                    self.window.open_file(full_readme_path)
                    sublime.status_message(f"Created README.md at: {full_readme_path}")

    def is_enabled(self, paths=None, item_id=None, **kwargs):
        if item_id != None:
            return not self.hasREADME(paths)
        return True

    def is_visible(self, paths=None, item_id=None, **kwargs):
        if item_id != None:
            return not self.hasREADME(paths)
        return True

    def description(self, paths=None, item_id=None, **kwargs):
        return MAIN_MENU_LABEL
