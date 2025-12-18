import sublime
import sublime_plugin
import os
import sys

class GetSidebarFolderCommand(sublime_plugin.WindowCommand):
    def getSelectedPath(self, paths):
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

    def getSidebarPath(self):
        # Find which top-level folder contains the path
        folders = self.window.folders()
        top = folders[0] if folders else None

        return top

    def run(self, paths=None, returnPathType=0):
        selectedFolder = "No path was found!"
        if returnPathType == 0:
            selectedFolder = self.getSelectedPath(paths)
        elif returnPathType == 1:
            selectedFolder = self.getSidebarPath()

        # Show result: Show status/quick panel
        sublime.status_message("Selected path: " + selectedFolder)
        self.window.show_quick_panel([selectedFolder], None)
        return selectedFolder
