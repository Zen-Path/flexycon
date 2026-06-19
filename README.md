<div align="center">
    <img src="./docs/static/logo.svg" width=200 height=200 title="Flexycon Logo">
    <h1>Flexycon</h1>
    <p>Where configuration meets automation.</p>
</div>

Flexycon (from _flexible_ + _configuration_) is my personal configuration ecosystem.
Rather than maintaining a scattered collection of dotfiles and one-off scripts, Flexycon
provides a unified and tested system for managing configs, scripts, snippets, and shared
utilities.

This is an actively maintained, daily-driven project, so bugs are caught quickly, and
features don't take ages to be implemented.

- [Core Philosophy](#core-philosophy)
    - [Smart Templating](#smart-templating)
    - [Python-Driven Configuration](#python-driven-configuration)
    - [Thoroughly Tested](#thoroughly-tested)
- [Stack](#stack)
- [Setup](#setup)
    - [Dependencies](#dependencies)
    - [Installation](#installation)
    - [Daily Usage](#daily-usage)
- [Preview](#preview)
    - [MacOS](#macos)
    - [Linux (X11)](#linux-x11)
- [Templating Examples](#templating-examples)
- [Inspiration](#inspiration)

## Core Philosophy

Flexycon is built on the principle that configuration should be dynamic, type-safe, and
environment-aware.

### Smart Templating

By combining templating with a dotfile manager, Flexycon dynamically compiles exactly
what is needed for the current environment. This eliminates bloated configurations and
prevents cross-platform conflicts.

### Python-Driven Configuration

Static configuration formats (like INI or YAML) lack logical validation. Flexycon is
actively migrating towards a model where configurations are defined natively in Python:

- _Validation_: Settings are validated at the logic level before deployment.
- _Exporting_: Python generates and exports the final configuration into the specific
  format required by the target application.

### Thoroughly Tested

Flexycon treats configuration like production software, using `pytest` and lots of test
to verify scripts, deployment logic, and file generation. As more configurations are
migrated to Python, the test coverage will go up to ensure almost zero downtime.

## Stack

| Function            | Platform       | Application                                                    | Website                                    |
| ------------------- | -------------- | -------------------------------------------------------------- | ------------------------------------------ |
| Browser             | Cross-Platform | [Firefox](https://github.com/mozilla-firefox/firefox)          | [link](https://www.firefox.com/)           |
| Window Manager      | MacOS          | [yabai](https://github.com/asmvik/yabai)                       | -                                          |
| Window Manager      | X11            | [dwm](https://github.com/Zen-Path/dwm-flexipatch)              | [link](https://dwm.suckless.org/)          |
| Status Bar          | X11            | [dwmblocks-async](https://github.com/Zen-Path/dwmblocks-async) | -                                          |
| Terminal            | MacOS          | [Kitty](https://github.com/kovidgoyal/kitty)                   | [link](https://sw.kovidgoyal.net/kitty/)   |
| Terminal            | X11 + Windows  | [Alacritty](https://github.com/alacritty/alacritty)            | [link](https://alacritty.org/)             |
| Shell               | Linux + MacOS  | [zsh](https://github.com/zsh-users/zsh)                        | [link](https://www.zsh.org/)               |
| Shell               | Windows        | [bash](https://ftp.gnu.org/gnu/bash/)                          | [link](https://www.gnu.org/software/bash/) |
| GUI Text Editor     | Cross-Platform | [Visual Studio Code](https://github.com/microsoft/vscode)      | [link](https://code.visualstudio.com/)     |
| CLI Text Editor     | Cross-Platform | [Neovim](https://github.com/neovim/neovim)                     | [link](https://neovim.io/)                 |
| File Manager        | Cross-Platform | [yazi](https://github.com/sxyazi/yazi)                         | [link](https://yazi-rs.github.io/)         |
| GUI Prompter        | MacOS          | [choose](https://github.com/chipsenkbeil/choose)               | -                                          |
| GUI Prompter        | X11            | [dmenu](https://github.com/Zen-Path/dmenu-flexipatch)          | [link](https://tools.suckless.org/dmenu/)  |
| Notification Daemon | Linux          | [Dunst](https://github.com/dunst-project/dunst)                | [link](https://dunst-project.org/)         |
| Image Viewer        | X11            | [nsxiv](https://github.com/Zen-Path/nsxiv)                     | [link](https://codeberg.org/nsxiv/nsxiv)   |
| PDF Viewer          | Linux          | [zathura](https://github.com/pwmt/zathura)                     | [link](https://pwmt.org/projects/zathura/) |
| Media Player        | Unix           | [mpv](https://github.com/mpv-player/mpv)                       | [link](https://mpv.io/)                    |

Additional integrations include:
[bottom](https://github.com/ClementTsang/bottom),
[gallery-dl](https://github.com/mikf/gallery-dl),
[newsraft](https://codeberg.org/grisha/newsraft),
[starship](https://github.com/starship/starship),
[yt-dlp](https://github.com/yt-dlp/yt-dlp),
and more.

## Setup

### Dependencies

Make sure you have the following installed:

- `git`
- `python >= 3.13`

### Installation

Clone the repository and run the bootstrap script:

```sh
git clone "https://github.com/Zen-Path/flexycon"
cd flexycon
./bootstrap.sh
```

### Daily Usage

When you update your configuration files, compile and deploy them by running:

```sh
flexy install
```

If you are testing changes to the Python virtual environment, or just need to wipe the slate clean, run:

```sh
flexy clean
```

Make sure the Python venv is active.

Later on, when you've made some changes to your config and want to apply them, run ``.

When testing changes to the venv, or just need a clean slate, run `` and it will do just that.

NOTE: The recommended installation path for Flexycon is `~/.local/src/flexycon`. If you
choose a custom location, ensure you update the `FLEXYCON_HOME` environmental variable.

## Preview

### MacOS

<img src="./docs/static/mac_full-screen.png" title="MacOS Full Screen">

### Linux (X11)

<img src="./docs/static/linux_full-screen.png" title="Linux Full Screen">

## Templating Examples

```sh
# Per-platform config
{%@@- if os == "darwin" +@@%}
export TERMINAL='kitty'
{%@@- elif os == "linux" +@@%}
export TERMINAL='alacritty'
{%@@- endif +@@%}

# Per-profile config
{%@@- if "home" in profile +@@%}
alias je='journal_entry'
{%@@- endif +@@%}

# Environmental variables substitutions
editor = '{{@@ env["EDITOR"] @@}}'

# Modular file importing
{%@@ include 'config/zsh/shortcuts.sh' @@%}
```

## Inspiration

Special thanks to Luke Smith and his [voidrice](https://lukesmith.xyz/) repository.
