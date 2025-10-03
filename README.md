# flexycon

Flexible programmatic configuration.

- [flexycon](#flexycon)
- [Setup](#setup)
    - [Dependencies](#dependencies)
    - [Installation](#installation)
- [Gallery](#gallery)
    - [Mac](#mac)
    - [Linux](#linux)

# Setup

## Dependencies

Make sure the following tools are installed:

- `python >= 3.13` (install via [Homebrew](https://brew.sh))
- `npm` - JavaScript package manager
- `make` - build automation tool
- `dotdrop` - dotfiles manager

## Installation

To install and initialize the project:

```sh
git clone "https://github.com/Zen-Path/flexycon"
cd flexycon
make setup
make install
```

To install the dotfiles in the correct location, follow these steps:

```sh
# From the top level of this repository:
dotdrop install

# Open a new terminal or source your updated shell configuration:
user_shortcuts

# Re-run the installation to apply the generated user shortcuts:
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
