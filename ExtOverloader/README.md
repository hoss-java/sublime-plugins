# Extension Overloader Plugin for Sublime Text
**Extension Overloader** is a Sublime Text plugin that sets syntax highlighting based on the file name and user-defined configuration. It allows you to specify syntax rules for files without extensions or with specific extensions according to patterns.

- Package - ExtOverloader
- Requiments - <None>

# Extension Overloader Plugin

## Introduction

The **Extension Overloader** is a Sublime Text plugin that intelligently sets the syntax highlighting for files based on their names and extensions. This plugin enhances your coding experience by applying the correct syntax highlighting rules, saving you time and preventing confusion while editing files.

## Features

- Automatically sets the syntax highlighting for files without extensions based on predefined patterns.
- Supports files with specific extensions using customizable configurations.
- Allows users to define their own matching patterns and associated syntax highlighting.

## Installation

1. Clone this repository or download the `ExtOverloader` file.
2. Place the `ExtOverloader` file in your `Packages/` directory within Sublime Text.

## Configuration

The plugin reads configuration settings from a file named `extension_oveloader.sublime-settings`. Here’s how to set it up:

1. Create a `extension_oveloader-settings` file in your `Packages/ExtOverloader` directory if it doesn’t exist.
2. Use the following structure to add your custom configurations:
```json
{
   "config": [
       {
           "path": "your/file/path",
           "pattern": "your\_regex\_pattern",
           "extension": "your\_file\_extension",
           "syntax": "Packages/YourSyntax/YourSyntax.sublime-syntax"
       }
       // Add more entries as needed
   ]
}
```

* Example Configuration
```json
{
    "config": [
        {
            "path": "src/",
            "pattern": "^.\*\\\.txt$",
            "extension": "",
            "syntax": "Packages/Markdown/Markdown.sublime-syntax"
        },
        {
            "path": "scripts/",
            "pattern": "^.\*\\\.sh$",
            "extension": ".sh",
            "syntax": "Packages/ShellScript/ShellScript.sublime-syntax"
        }
    ]
}
```

* In this example, .txt files in the src/ directory will be treated as Markdown files, while .sh files in the scripts/ directory will have the Shell Script syntax applied.

## Usage

Once the plugin is installed and configured, it will automatically activate the appropriate syntax highlighting when you open a file matching the defined configurations. You don't have to do anything else; just open your files and start coding!

## Support

If you encounter issues or have suggestions for improvements, feel free to raise an issue in the repository or contact the author directly.

## License

This plugin is released under the MIT License. See the LICENSE file for more information.