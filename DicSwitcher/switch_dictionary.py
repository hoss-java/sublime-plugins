import sublime
import sublime_plugin

class SetDictionaryCommand(sublime_plugin.ApplicationCommand):
    def run(self, path):
        print("SetDictionaryCommand:", path)
        settings = sublime.load_settings("Preferences.sublime-settings")
        settings.set("dictionary", path)
        sublime.save_settings("Preferences.sublime-settings")
        sublime.status_message("Dictionary set: " + path)
