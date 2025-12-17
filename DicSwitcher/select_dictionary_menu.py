import sublime, sublime_plugin, os, json, zipfile, traceback

PACKAGE_NAME = "DicSwitcher"
MENU_FILENAME = "Context.sublime-menu"
DICT_PACKAGE = "Dictionaries"  # folder under Packages containing .dic files

def log(msg):
    print("[DicSwitcher]", msg)

def list_dic_files():
    dic_files = []
    # 1) Filesystem: Packages/Dictionaries
    fs_dir = os.path.join(sublime.packages_path(), DICT_PACKAGE)
    if os.path.isdir(fs_dir):
        for name in sorted(os.listdir(fs_dir)):
            if name.lower().endswith(".dic"):
                dic_files.append(os.path.join("Packages", DICT_PACKAGE, name))

    # 2) Inspect Installed Packages archives for .dic files
    installed = sublime.installed_packages_path()
    if os.path.isdir(installed):
        for fname in os.listdir(installed):
            if not fname.lower().endswith(".sublime-package"):
                continue
            fp = os.path.join(installed, fname)
            try:
                with zipfile.ZipFile(fp, "r") as z:
                    for zi in z.namelist():
                        if zi.lower().endswith(".dic"):
                            name = os.path.basename(zi)
                            path = os.path.join("Packages", DICT_PACKAGE, name)
                            if path not in dic_files:
                                dic_files.append(path)
            except Exception:
                log("zip read error: " + fp)
    return dic_files

def build_menu(children):
    return [
        {
            "id": "select_dictionary",
            "caption": "Select Dictionary",
            "children": children
        }
    ]

def get_current_dictionary():
    s = sublime.load_settings("Preferences.sublime-settings").get("dictionary", "")
    return os.path.normpath(os.path.join(sublime.packages_path(), s[len("Packages/"):])) if s.startswith("Packages/") else os.path.normpath(s)

def build_children(dic_paths):
    current = get_current_dictionary()
    children = []
    for p in dic_paths:
        full = os.path.normpath(os.path.join(sublime.packages_path(), p[len("Packages/"):]))
        label = os.path.splitext(os.path.basename(p))[0]
        item = {"caption": label, "command": "set_dictionary", "args": {"path": p}}
        if full == current:
            item["checked"] = True
            label = label+"✓ "
        item["caption"] = label
        children.append(item)
    return children


def write_menu_file(children):
    try:
        pkg_path = os.path.join(sublime.packages_path(), PACKAGE_NAME)
        os.makedirs(pkg_path, exist_ok=True)
        menu_path = os.path.join(pkg_path, MENU_FILENAME)
        menu = build_menu(children)
        with open(menu_path, "w", encoding="utf-8") as f:
            json.dump(menu, f, indent=4, ensure_ascii=False)
        log("Wrote menu with %d items" % len(children))
    except Exception:
        log("Error writing menu: " + traceback.format_exc())

def populate_menu():
    try:
        dic_paths = list_dic_files()
        children = build_children(dic_paths)
        write_menu_file(children)
    except Exception:
        log("Populate error: " + traceback.format_exc())

class DicSwitcherLoader():
    @staticmethod
    def plugin_loaded():
        populate_menu()

# Call on plugin load
try:
    populate_menu()
except Exception:
    log("Initial populate failed: " + traceback.format_exc())

class PopulateOnEvents(sublime_plugin.EventListener):
    # context menu opening does not provide a dedicated event; use activation/window command events
    def on_activated(self, view):
        populate_menu()

    def on_window_command(self, window, command_name, args):
        # ensure menu is up-to-date when many window commands run (cheap check)
        populate_menu()
        return None
