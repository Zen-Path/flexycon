<div align="center">
    <img src="./docs/static/logo.svg" width=200 height=200>
    <h1>Flexycon</h1>
    <p>🧩 Where configuration meets automation 💡</p>
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

## Installation

To install and initialize the project:

```sh
git clone "https://github.com/Zen-Path/flexycon"
cd flexycon
./bootstrap.sh
```

Later on, when you've made some changes to your config and want to apply them, run `flexy install`.

When testing changes to the venv, or just need a clean slate, run `flexy clean` and it will do just that.

NOTE: the recommended location for installing flexycon is `~/.local/src/flexycon`, but if you've installed it
somewhere else, update the `FLEXYCON_HOME` environmental variable.

# Gallery

## Mac

![Full Screen](./docs/static/mac_full-screen.png "Full screen")

## Linux

![Full Screen](./docs/static/linux_full-screen.png "Full screen")
