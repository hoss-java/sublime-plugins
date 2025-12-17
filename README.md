# Sublime-text plugins

## The Plugins quick overviews
### DicSwitcher
README -> https://github.com/hoss-java/sublime-plugins/blob/main/DicSwitcher/README.md

### MarkdownXtra
README -> https://github.com/hoss-java/sublime-plugins/blob/main/MarkdownXtra/README.md

### WhiteSpaces
README -> https://github.com/hoss-java/sublime-plugins/blob/main/WhiteSpaces/README.md

### Maven
README -> https://github.com/hoss-java/sublime-plugins/blob/main/Maven/README.md

## Improving Sublime env to precede
### Lines prediction
Markdown colorize markdown and other tagged file formats but it does precede text on a new line (added by Enter) based on the current line.

As I found it needs to code a new plugin, to add a new plug-in Tools → Developer → New Plug-in, then replace the code with the code below and save it with an appropriate name such as `Packages/MarkdownXtra/continue_markdown.py`
```
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
```

OBS! All files packed in a folder named **MarkdownXtra**

### Speller check languages
I'm not good on spelling words. There are usually many misspell on my texts. Sublime has a nice speller check and I have already added a hotkey to enable/disable the speller checker quickly but according to use a multi-languages system/keyboard it needs to add a new key to switch between speller checkers (using menus take time!!).

To add a function/key to switch between languages used by Sublime speller checker it needs to add a simple plug-in first
> * `Packages/DicSwitcher/switch_dictionary.py`
>>```
>>import sublime
>>import sublime_plugin
>>
>>class SetDictionaryCommand(sublime_plugin.ApplicationCommand):
>>    def run(self, path):
>>        settings = sublime.load_settings("Preferences.sublime-settings")
>>        settings.set("dictionary", path)
>>        sublime.save_settings("Preferences.sublime-settings")
>>        sublime.status_message("Dictionary set: " + path)
>>```

Now it needs to bind keys for languages, Preferences → Key bindings
```
[
    {
        "keys": ["ctrl+shift+s"],
        "command": "toggle_setting",
        "args": { "setting": "spell_check" }
    },
    {
        "keys": ["ctrl+alt+1"],
        "command": "set_dictionary",
        "args": { "path": "Packages/Dictionaries/English (American).dic" }
    },
    {
        "keys": ["ctrl+alt+2"],
        "command": "set_dictionary",
        "args": { "path": "Packages/Dictionaries/Swedish.dic" }
    }
]
``````

OBS! All files packed in a folder named **DicSwitcher**

### Whitespaces
Another problem for both texts and codes are whitespaces. As I know Sublime has an internal functionality to see and fixing white spaces but it seems it does not work in my case!

OBS! All files packed in a folder named **WhiteSpaces**

### Maven

OBS! All files packed in a folder named **Maven**