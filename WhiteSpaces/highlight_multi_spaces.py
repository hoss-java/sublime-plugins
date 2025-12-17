import sublime
import sublime_plugin
import re

REGIONS_KEY = "multi_spaces_regions"
SPACE_RUN_RE = r' {2,}'           # general runs of 2+ spaces
TRAILING_RE = r' {2,}$'           # trailing spaces at EOL
FENCE_RE = re.compile(r'^\s*(`{3,}|~{3,})')  # fenced code fence

def is_inside_fenced_block(view, row):
    # scan backward to nearest fence; odd count => inside
    # This is a simple heuristic reading lines; robust enough for usual fenced blocks.
    fence_count = 0
    for r in range(row, -1, -1):
        line = view.substr(view.line(view.text_point(r, 0)))
        m = FENCE_RE.match(line)
        if m:
            fence_count += 1
    return (fence_count % 2) == 1

def strip_leading_blockquotes_and_spaces(line, tab_size, translate):
    # Remove leading '>' markers and following spaces. Return the stripped line and number of chars removed.
    orig = line
    removed = 0
    idx = 0
    # remove repeating blockquote markers with optional spaces: ">", "> ", ">> ", etc.
    while idx < len(line):
        if line[idx] == '>':
            idx += 1
            # consume following single space if present
            if idx < len(line) and line[idx] == ' ':
                idx += 1
            continue
        # consume leading spaces after all > markers
        if line[idx] == ' ':
            idx2 = idx
            while idx2 < len(line) and line[idx2] == ' ':
                idx2 += 1
            removed = idx2
        break
    stripped = line[idx:]
    return stripped, idx

def find_regions(view):
    regions = []
    tab_size = int(view.settings().get("tab_size", 4))
    translate = bool(view.settings().get("translate_tabs_to_spaces", False))
    total_lines = view.rowcol(view.size())[0] + 1

    # first, trailing spaces anywhere
    for r in view.find_all(TRAILING_RE):
        regions.append(r)

    # find runs of spaces
    for r in view.find_all(SPACE_RUN_RE):
        # get line and row/col
        line_region = view.line(r)
        line_text = view.substr(line_region)
        row, col = view.rowcol(r.a)

        # skip if inside fenced code block
        if is_inside_fenced_block(view, row):
            continue

        # strip leading blockquote markers '>' and following spaces (adjust column)
        stripped, removed_chars = strip_leading_blockquotes_and_spaces(line_text, tab_size, translate)
        # compute match start relative to line start
        start_in_line = (r.a - line_region.a)
        # if match lies within removed prefix area, treat as indentation and skip
        if start_in_line < removed_chars:
            continue

        # if translate_tabs_to_spaces is true, skip matches that are within leading indentation composed of repeated tab_size spaces
        if translate:
            # count leading spaces after blockquotes
            # compute how many leading spaces (after > markers) the original line has
            # find index of first non-space after removed blockquote markers
            prefix = line_text[:removed_chars]
            leading_after_bq = len(line_text[removed_chars:]) - len(line_text[removed_chars:].lstrip(' '))
            # If the match starts before or within that leading_after_bq, and leading_after_bq is multiple of tab_size, skip
            if start_in_line < removed_chars + leading_after_bq:
                # if the leading spaces align to tab_size blocks, skip
                if leading_after_bq % tab_size == 0:
                    continue

        # ignore pure indentation at column 0 (no other chars on line)
        if start_in_line == 0 and line_text.strip() == '':
            continue

        # otherwise accept region (but if the found region overlaps removed prefix we already skipped)
        regions.append(r)

    # unique
    seen = set()
    out = []
    for reg in regions:
        key = (reg.a, reg.b)
        if key not in seen:
            seen.add(key)
            out.append(reg)
    return out

class HighlightMultiSpacesListener(sublime_plugin.EventListener):
    def maybe_update(self, view):
        enabled = sublime.load_settings("Preferences.sublime-settings").get("highlight_multi_spaces_enabled", True)
        if not enabled:
            view.erase_regions(REGIONS_KEY)
            return
        regions = find_regions(view)
        view.erase_regions(REGIONS_KEY)
        if regions:
            view.add_regions(REGIONS_KEY, regions, scope="invalid.deprecated.trailing-whitespace", flags=sublime.DRAW_NO_OUTLINE)

    def on_modified_async(self, view):
        self.maybe_update(view)
    def on_activated_async(self, view):
        self.maybe_update(view)

class ToggleHighlightMultiSpacesCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        s = sublime.load_settings("Preferences.sublime-settings")
        cur = s.get("highlight_multi_spaces_enabled", True)
        s.set("highlight_multi_spaces_enabled", not cur)
        sublime.save_settings("Preferences.sublime-settings")
        for w in sublime.windows():
            for v in w.views():
                if not cur:
                    # turn on
                    regions = find_regions(v)
                    if regions:
                        v.add_regions(REGIONS_KEY, regions, scope="invalid.deprecated.trailing-whitespace", flags=sublime.DRAW_NO_OUTLINE)
                else:
                    v.erase_regions(REGIONS_KEY)
        sublime.status_message("Highlight multi-spaces: " + ("ON" if not cur else "OFF"))
