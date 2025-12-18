import sublime
import sublime_plugin
import json, os, sys, time
from typing import List, Optional

# --- Configuration ---
PACKAGE = "Maven"
MENU_PATH = os.path.join(sublime.packages_path(), PACKAGE, "Side Bar.sublime-menu")
# Name used in the sidebar context menu
MAVEN_MENU_LABEL = "Maven"
# If True, will add a disabled menu entry when docker not found.
SHOW_DISABLED_WHEN_NOT_FOUND = False

mavenMenuPlaceholder = False
# --- End config ---

def write_maven_menu():
    menu = [
        {
            "caption": MAVEN_MENU_LABEL,
            "command": "maven_menu_placeholder",
            "children": [
                {
                    "caption": "Get Folder Path (absolute)",
                    "command": "get_sidebar_folder",
                    "args": {"paths": ["$folder"],"returnPathType":0}
                },
                {
                    "caption": "Get Sidebar Path (absolute)",
                    "command": "get_sidebar_folder",
                    "args": {"paths": ["$folder"],"returnPathType":1}
                },
                {
                    "caption": "Get Folder Path (relative)",
                    "command": "get_sidebar_folder",
                    "args": {"paths": ["$folder"],"returnPathType":2}
                }
            ]
        }
    ]
    os.makedirs(os.path.dirname(MENU_PATH), exist_ok=True)
    with open(MENU_PATH, "w", encoding="utf-8") as f:
        json.dump(menu, f, indent=2, ensure_ascii=False)

# Run initial check in background so startup isn't blocked
def plugin_loaded():
    global mavenMenuPlaceholder

    mavenMenuPlaceholder = True
    write_maven_menu()

class MavenMenuPlaceholderCommand(sublime_plugin.WindowCommand):
    # This command exists only so the menu group can be enabled/disabled
    def run(self):
        # No action; group acts as a placeholder
        pass

    def is_enabled(self):
        return mavenMenuPlaceholder

    def is_visible(self):
        # Always visible so the menu header shows even when disabled
        return True

    def description(self, **kwargs):
        return MAVEN_MENU_LABEL

class GetSidebarFolderCommand(sublime_plugin.WindowCommand):
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

    def run(self, paths=None, returnPathType=0) -> Optional[str]:
        requestedPath = "No path was found!"
        if returnPathType == 0:
            selectedFolder = self.getSelectedPath(paths)
            if selectedFolder != None:
                requestedPath = selectedFolder
        elif returnPathType == 1:
            windowFolder = self.getSidebarPath()
            if windowFolder != None:
                requestedPath = windowFolder
        elif returnPathType == 2:
            selectedFolder = self.getSelectedPath(paths)
            windowFolder = self.getSidebarPath()
            relativePath = self.getRelativePath(selectedFolder,windowFolder)
            if relativePath != None:
                requestedPath = relativePath 

        # Show result: Show status/quick panel
        sublime.status_message("Requested path: " + requestedPath)
        self.window.show_quick_panel([requestedPath], None)
        return requestedPath
