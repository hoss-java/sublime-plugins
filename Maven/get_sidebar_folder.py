import sublime
import sublime_plugin
import os
import sys
from typing import List, Optional

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
