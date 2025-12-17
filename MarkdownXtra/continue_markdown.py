import re
import sublime
import sublime_plugin

class ContinueMarkdownOnEnter(sublime_plugin.EventListener):
    def on_text_command(self, view, command_name, args):
        # only act when Enter is pressed
        if command_name != "insert" or args.get("characters") != "\n":
            return None

        # get current caret (primary sel)
        sel = view.sel()[0]
        pt = sel.b
        line_region = view.line(pt)
        line_text = view.substr(line_region)

        # patterns to capture common markdown prefixes
        patterns = [
            r'^(\s*>+\s*)',                          # blockquote (>, >>, etc.)
            r'^(\s*[-+*]\s+)',                       # bullet list -, +, *
            r'^(\s*\d+\.\s+)',                       # numbered list 1. 2. ...
            r'^(\s*```.*$)',                         # fenced code start (keep same fence)
            r'^(\s*>\s*$)',                          # single '>' with no text
            r'^(\s*-\s*$|\s*\*\s*$|\s*\+\s*$)',      # bullets with no text
        ]

        prefix = ""
        # check fenced code separately: if line starts with ``` keep same fence on new line
        m = re.match(r'^(\s*`{3,}[^`]*)', line_text)
        if m:
            prefix = m.group(1)
            # If the fenced line is just the fence and it's opening, don't auto-insert inside code block content.
            return ("insert_snippet", {"contents": "\n" + prefix})

        for pat in patterns:
            m = re.match(pat, line_text)
            if m:
                prefix = m.group(1)
                break

        # numbered list: if matches number. increment next number
        mnum = re.match(r'^(\s*)(\d+)\.(\s+)', line_text)
        if mnum:
            indent, num, spacer = mnum.group(1), int(mnum.group(2)), mnum.group(3)
            next_num = num + 1
            contents = "\n" + indent + str(next_num) + "." + spacer
            return ("insert_snippet", {"contents": contents})

        if prefix:
            return ("insert_snippet", {"contents": "\n" + prefix})

        return None
