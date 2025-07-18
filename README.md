# flexycon

Flexible programmatic configuration.

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

# Tips

### Mac sleep enable / disable

Enable:

```sh
sudo pmset -a disablesleep 0
```

Source: https://gist.github.com/laurion/d93eb70efcc6f3b3716173c94e74f435

### Monday as first day of the week

1. Open `/etc/locale.conf` and change `LC_TIME` to `en_DK.UTF-8` (Denmark)
2. Open `/etc/locale.gen` and uncomment `en_DK.UTF-8`
3. Regenerate locales by running:

```sh
sudo locale-gen
```

4. Reboot
5. Run `cal`. It should display 'Mon' as first day of the week.

### Check available locales

Run:

```sh
locale -a
```

### Check current locale settings

Run:

```sh
locale
```

### Extract only matches using rg

Run:

```sh
rg --only-matching 'pattern: (\d+)' --replace '$1'
```

## TODO

- [Emmet](https://www.emmet.io/) for nvim / emacs

### Replacements

- Zathura
- dwmblocks
