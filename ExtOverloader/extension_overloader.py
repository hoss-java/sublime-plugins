import sublime
import sublime_plugin
import os
import re

class SetSyntaxForDigitsCommand(sublime_plugin.EventListener):
    def on_load(self, view):
        file_name = view.file_name()

        if file_name:  # Ensure that the file name is available
            base_name = os.path.basename(file_name)  # Get the base name of the file

            # Load the settings
            settings = sublime.load_settings("ShellInc.sublime-settings")
            config = settings.get("config", [])  # Get the config, default to empty list

            # Check each configuration
            for entry in config:
                if entry["path"] in file_name:
                    if (entry["extension"] == "" and re.match(entry["pattern"], base_name) and not base_name.startswith('.')):
                        # Set Markdown syntax for allowed paths with no extension
                        view.set_syntax_file(entry["syntax"])
                    elif re.match(entry["pattern"], base_name) and not base_name.startswith('.') and os.path.splitext(base_name)[1] == entry["extension"]:
                        # Set Shell script syntax for allowed paths with specified extension
                        view.set_syntax_file(entry["syntax"])
