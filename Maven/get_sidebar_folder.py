import sublime
import sublime_plugin
import os
import sys

class GetSidebarFolderCommand(sublime_plugin.WindowCommand):
    def run(self, paths=None):
        # Expect 'paths' from Side Bar menu args (["$file"] or ["$folder"])
        if not paths:
            # fallback to active file
            view = self.window.active_view()
            if view and view.file_name():
                paths = [view.file_name()]
            else:
                sublime.message_dialog("No path provided and no active file.")
                return

        # Accept a list; take first item
        path = paths[0]
        if isinstance(path, dict) and "path" in path:
            path = path["path"]
        if not path:
            sublime.message_dialog("Invalid path provided.")
            return

        if os.path.isdir(path):
            selectedFolder = path
        elif os.path.isfile(path):
            selectedFolder = os.path.dirname(path)
        else:
            sublime.message_dialog("Selected path does not exist: " + str(path))
            return

        # Show result: Show status/quick panel
        sublime.status_message("Selected path: " + selectedFolder)
        self.window.show_quick_panel([selectedFolder], None)
        return selectedFolder
