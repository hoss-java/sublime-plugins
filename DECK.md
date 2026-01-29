---
Title: sublime-plugins
Description: plans and project management sheets
Date: 
Robots: noindex,nofollow
Template: index
---

# sublime-plugins

## Analyzing all parts

|#|Part|Details|Total Duration|Status|
|:-|:-|:-|:-|:-|
|1|-|-|-|-|-|
|:-|:-|:-|::||


## Timeplan

```mermaid
gantt
    section %BOARD%
```

# 1 - containers

## 001-0001
> **DicSwitcher** ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> <details >
>     <summary>Details</summary>
> The goal of this card is add a new plugin to Sublime to make it easy to switch between languages
> 
> # DOD (definition of done):
> Add some hotkeys to switch between Swedish and english
> Finings are documented.
> 
> # TODO:
> - [x] 1. Document all findings
> 
> # Reports:
> * To make faster to type and document readme(markdown) files without using external tools to spellcheck.
> </details>

## 001-0002
> **MarkdownXtra** ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> <details >
>     <summary>Details</summary>
> The goal of this card is to develop a sublime-text plugin to enhance working with markdown files.
> 
> # DOD (definition of done):
> All finings are documented.
> 
> # TODO:
> - [x] 1. Document all findings
> 
> # Reports:
> *
> </details>

## 001-0003
> **WhiteSpaces** ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> <details >
>     <summary>Details</summary>
> The goal of this card is to develop a sublime-text plugin to manage whitespaces.
> 
> # DOD (definition of done):
> All finings are documented.
> 
> # TODO:
> - [] 1. Document all findings
> 
> # Reports:
> *
> </details>

## 001-0004
> **Maven** ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> <details >
>     <summary>Details</summary>
> The goal of this card is to develop a sublime-text plugin to enhance working with Maven projects
> 
> # DOD (definition of done):
> All findings are documented.
> 
> # TODO:
> - [x] 1. Document all findings
> 
> # Reports:
> * Step 1 - Find the folder path right clicked on the side bar
> > * Find the root path of the side bar ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> > * Find absolute path of the selected item on the side bar ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> > * Find relative path of the selected item on the side bar ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> * Step 2 - Make the menu and other commands items dynamic
> > * Update the `get_sidebar_folder.py` to use as the Maven plugin base
> > * Change the static menu to a dynamic menu ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> > * Add path to the menu group title ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> * Step 3 - check a selected folder on the side bar is a Maven project folder/file
> > * A selected item is inside a Maven project if the current selected folder or one of upper level folders has a `pom.xml` stored in ![status](https://img.shields.io/badge/status-DONE-bri>
> > * The upper level folders are scanned to find `pom.xml` up to the root folder inside of the side bar ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> > * Perhaps a xml check for `pom.xml` is required ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> * Step 4 - Reading/saving settings
> > * Add a settings file and its loading method ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> * Step 5 - Adapt the Maven menu
> > * Re-code the menu part to make it easy to add new items ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> > * Check maven availability to enable disable menu items
> > * Assign commands to menu items and find appropriate path of the project according to the method to run maven (host base or container base)
> > * In the case of a container base maven if the project path cannot be converted to a known path for the container, the menu items are disabled
> > * Finalize command implementation and find a solutions or way to show command running outputs
> > * Work on the create command, adding types, and find how to ask the name of the project
> > * List features than can be added later, not now with this card
> </details>

## 001-0005
> **Add deck board to repo.** ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> <details >
>     <summary>Details</summary>
> The goal of this card is to add a deck board to the repo.
> 
> # DOD (definition of done):
> The repo has a deck board.
> guthub workflow and needed scripts are added.
> Repo has a secert token.
> 
> # TODO:
> - [x] 1. Install/init deck on the repo
> - [x] 2. Add gihub action files
> - [x] 3. Add a token the repo
> 
> # Reports:
> *
> </details>

## 001-0006
> **AddREADME** ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> <details >
>     <summary>Details</summary>
> The goal of this card is to develop a sublime plugin to add README to repo(s)
> 
> # DOD (definition of done):
> A sublime plugin to manage README is developed.
> 
> # TODO:
> - [x] 1. Develop plugin
> - [x} 2. Add some README templates
> 
> # Reports:
> *
> </details>

## 001-0007
> **Add github actions to repo.** ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> <details >
>     <summary>Details</summary>
> The goal of this card is to add github workflow to the repo.
> 
> # DOD (definition of done):
> A github workflow with an action to create DECK.md is added to the repo.
> 
> # TODO:
> - [X] 1. Add an action to create/generate DECK.md
> 
> # Reports:
> *
> </details>

## 001-0008
> **fix DicSwitcher issues.** ![status](https://img.shields.io/badge/status-DONE-brightgreen)
> <details >
>     <summary>Details</summary>
> The goal of this card is to fix issues found on DicSwitcher plugin.
> 
> # DOD (definition of done):
> Issues are fixed.
> 
> # TODO:
> - [ ] 1. Fix issues.
> 
> # Reports:
> *
> </details>
