<div align="center">
    <img src="./docs/static/logo.svg" width=200 height=200>
    <h1>Flexycon</h1>
    🧩 Where configuration meets automation 💡
</div>

Flexycon (from _flexible_ + _configuration_) is my personal configuration ecosystem — a unified system
for managing configs, scripts, snippets, and shared utilities.
Instead of isolated dotfiles or one-off scripts, every component is designed to work together and build
off of one another.

By combining templating and a dotfile manager, I ensure that only the configuration I actually need is
deployed — customized automatically for each environment.

Examples:

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

# Easy file importing — break large configs into smaller pieces
{%@@ include 'config/zsh/shortcuts.sh' @@%}
```

- [Setup](#setup)
    - [Dependencies](#dependencies)
    - [Installation](#installation)
- [Gallery](#gallery)
    - [Mac](#mac)
    - [Linux](#linux)

# Setup

## Dependencies

Make sure you have the following installed:

- `git`
- `python >= 3.13`
- `make`

## Installation

To install and initialize the project:

```sh
git clone "https://github.com/Zen-Path/flexycon"
cd flexycon
make setup
make install
dotdrop install
```

When testing changes to the venv, or just needing a clean slate, you can use `make clean` and it will clean up the project a bit.

# Gallery

## Mac

![Full Screen](./docs/static/mac-full-screen.png "Full Screen")

## Linux

The Linux config is found in the `linux-android-profiles` branch.

Tile Layout:

![Tile Layout](./docs/static/full-screen_tile.png "Tile Layout")

Centered Master Layout:

![Centered Master Layout](./docs/static/full-screen_centered-master.png "Centered Master Layout")
