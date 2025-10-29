import os

from common.packages.package_managers import Brew, Package, Yay

packages = [
    Package(
        identifier="bat",
        managers=[Brew],
        description="cat(1) clone with syntax highlighting and Git integration",
    ),
    Package(
        identifier="bottom",
        managers=[Brew],
        description="Yet another cross-platform graphical process/system monitor",
    ),
    Package(
        identifier="dust",
        managers=[Brew],
        description="More intuitive version of du in rust",
    ),
    Package(
        identifier="exiftool",
        managers=[Brew],
        description="Perl lib for reading and writing EXIF metadata",
    ),
    Package(
        identifier="fd",
        managers=[Brew],
        description="Simple, fast and user-friendly alternative to find",
    ),
    Package(
        identifier="ffmpeg",
        managers=[Brew],
        description="Play, record, convert, and stream audio and video",
    ),
    Package(
        identifier="firefox",
        managers=[Brew],
        is_gui=True,
        description="Free and open source web browser",
    ),
    Package(
        identifier="fzf",
        managers=[Brew],
        description="Fuzzy finder in the terminal",
    ),
    Package(
        identifier="ghostscript",
        managers=[Brew],
        description="Interpreter for PostScript and PDF",
    ),
    Package(
        identifier="git",
        managers=[Brew],
        description="Distributed revision control system",
    ),
    Package(
        identifier="imagemagick",
        managers=[Brew],
        description="Tools and libraries to manipulate images in many formats",
    ),
    Package(
        identifier="kitty",
        managers=[Brew],
        is_gui=True,
        description="GPU-based terminal emulator",
    ),
    Package(
        identifier="mpv",
        managers=[Brew],
        description="Media player based on MPlayer and mplayer2",
    ),
    Package(
        name="NeoVim",
        identifier="neovim",
        managers=[Brew],
        description="Ambitious Vim-fork focused on extensibility and agility",
    ),
    Package(
        identifier="newsraft",
        managers=[Brew],
        description="Terminal feed reader",
    ),
    Package(
        identifier="node",
        managers=[Brew],
        description="JS platform built on V8 to build network applications",
    ),
    Package(
        identifier="prettier",
        managers=[Brew],
        description="Code formatter for JavaScript, CSS, JSON, GraphQL, Markdown, YAML",
    ),
    Package(
        identifier="rclone",
        managers=[Brew],
        description="Rsync for cloud storage",
    ),
    Package(
        identifier="ripgrep",
        managers=[Brew],
        description="Search tool like grep and The Silver Searcher",
    ),
    Package(
        identifier="ripgrep-all",
        managers=[Brew],
        description="Wrapper around ripgrep that adds multiple rich file types",
    ),
    Package(
        identifier="shfmt",
        managers=[Brew],
        description="Autoformat shell script source code",
    ),
    Package(
        identifier="sqlite",
        managers=[Brew],
        description="Command-line interface for SQLite",
    ),
    Package(
        identifier="starship",
        managers=[Brew],
        description="Cross-shell prompt for astronauts",
    ),
    Package(
        identifier="stylua",
        managers=[Brew],
        description="Opinionated Lua code formatter",
    ),
    Package(
        identifier="taplo",
        managers=[Brew],
        description="TOML toolkit written in Rust",
    ),
    Package(
        identifier="telegram",
        managers=[Brew],
        is_gui=True,
        description="Messaging app with a focus on speed and security",
    ),
    Package(
        identifier="tree",
        managers=[Brew],
        description="Display directories as trees (with optional color/HTML output)",
    ),
    Package(
        name="Visual Studio Code",
        identifier="visual-studio-code",
        managers=[Brew],
        is_gui=True,
        description="GUI code editor developed by Microsoft",
    ),
    Package(
        identifier="yazi",
        managers=[Brew],
        description="Blazing fast terminal file manager written in Rust, based on async I/O",
    ),
    Package(
        identifier="yt-dlp",
        managers=[Brew],
        description="Feature-rich command-line audio/video downloader",
    ),
    Package(
        identifier="zip",
        managers=[Brew],
        description="Compression and file packaging/archive utility",
    ),
    Package(
        identifier="zsh-fast-syntax-highlighting?",
        managers=[Brew],
        description="Feature-rich syntax highlighting for Zsh",
        condition=os.environ["SHELL"] == "/bin/zsh",
    ),
    Package(identifier="dunst", managers=[Yay]),
    Package(identifier="gruvbox-dark-gtk", managers=[Yay]),
    Package(identifier="maim", managers=[Yay]),
    Package(identifier="pamixer", managers=[Yay]),
    Package(identifier="pulsemixer", managers=[Yay]),
    Package(identifier="taskwarrior-tui", managers=[Yay]),
    Package(identifier="trash-cli", managers=[Yay]),
    Package(identifier="ueberzugpp", managers=[Yay]),
    Package(
        identifier="unzip",
        managers=[Yay],
        description="Extraction utility for .zip compressed archives",
    ),
    Package(identifier="xcompmgr", managers=[Yay]),
    Package(identifier="xdotool", managers=[Yay]),
    Package(identifier="xorg-server", managers=[Yay]),
    Package(identifier="xorg-xev", managers=[Yay]),
    Package(identifier="xorg-xinit", managers=[Yay]),
    Package(identifier="xwallpaper", managers=[Yay]),
    Package(identifier="zathura-pdf-poppler", managers=[Yay]),
]
