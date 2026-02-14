import sublime, sublime_plugin

MODES_ST4 = ["all", "selection", "none"]
MODES_LEGACY = ["all", "none"]

def supports_selection():
    # Try setting then reading back to detect support
    s = sublime.load_settings("Preferences.sublime-settings")
    orig = s.get("draw_white_space", None)
    s.set("draw_white_space", "selection")
    sublime.save_settings("Preferences.sublime-settings")
    read_back = s.get("draw_white_space", None)
    # restore original
    if orig is None:
        s.erase("draw_white_space")
    else:
        s.set("draw_white_space", orig)
    sublime.save_settings("Preferences.sublime-settings")
    return read_back == "selection"

class ShowWhiteSpaceCycleCommand(sublime_plugin.WindowCommand):
    def run(self):
        s = sublime.load_settings("Preferences.sublime-settings")
        cur = s.get("draw_white_space", "none")
        if supports_selection():
            modes = MODES_ST4
        else:
            modes = MODES_LEGACY
        try:
            i = modes.index(cur)
            nxt = modes[(i + 1) % len(modes)]
        except ValueError:
            nxt = modes[0]
        s.set("draw_white_space", nxt)
        sublime.save_settings("Preferences.sublime-settings")
        sublime.status_message("Show WhiteSpace: " + nxt)
