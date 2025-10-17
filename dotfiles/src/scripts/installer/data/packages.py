import os

from scripts.installer.src.models import Brew, Package, Yay

packages = [
    Package(
        identifier="bat",
        manager=Brew,
        description="cat(1) clone with syntax highlighting and Git integration",
    ),
    Package(
        identifier="bottom",
        manager=Brew,
        description="Yet another cross-platform graphical process/system monitor",
    ),
    Package(
        identifier="dust",
        manager=Brew,
        description="More intuitive version of du in rust",
    ),
    Package(
        identifier="exiftool",
        manager=Brew,
        description="Perl lib for reading and writing EXIF metadata",
    ),
    Package(
        identifier="fd",
        manager=Brew,
        description="Simple, fast and user-friendly alternative to find",
    ),
    Package(
        identifier="ffmpeg",
        manager=Brew,
        description="Play, record, convert, and stream audio and video",
    ),
    Package(
        identifier="firefox",
        manager=Brew,
        description="Free and open source web browser",
    ),
    Package(
        identifier="fzf",
        manager=Brew,
        description="Fuzzy finder in the terminal",
    ),
    Package(
        identifier="ghostscript",
        manager=Brew,
        description="Interpreter for PostScript and PDF",
    ),
    Package(
        identifier="git",
        manager=Brew,
        description="Distributed revision control system",
    ),
    Package(
        identifier="imagemagick",
        manager=Brew,
        description="Tools and libraries to manipulate images in many formats",
    ),
    Package(
        identifier="kitty",
        manager=Brew,
        description="GPU-based terminal emulator",
    ),
    Package(
        identifier="mpv",
        manager=Brew,
        description="Media player based on MPlayer and mplayer2",
    ),
    Package(
        name="NeoVim",
        identifier="neovim",
        manager=Brew,
        description="Ambitious Vim-fork focused on extensibility and agility",
    ),
    Package(
        identifier="newsraft",
        manager=Brew,
        description="Terminal feed reader",
    ),
    Package(
        identifier="node",
        manager=Brew,
        description="JS platform built on V8 to build network applications",
    ),
    Package(
        identifier="prettier",
        manager=Brew,
        description="Code formatter for JavaScript, CSS, JSON, GraphQL, Markdown, YAML",
    ),
    Package(
        identifier="rclone",
        manager=Brew,
        description="Rsync for cloud storage",
    ),
    Package(
        identifier="ripgrep",
        manager=Brew,
        description="Search tool like grep and The Silver Searcher",
    ),
    Package(
        identifier="ripgrep-all",
        manager=Brew,
        description="Wrapper around ripgrep that adds multiple rich file types",
    ),
    Package(
        identifier="shfmt",
        manager=Brew,
        description="Autoformat shell script source code",
    ),
    Package(
        identifier="sqlite",
        manager=Brew,
        description="Command-line interface for SQLite",
    ),
    Package(
        identifier="starship",
        manager=Brew,
        description="Cross-shell prompt for astronauts",
    ),
    Package(
        identifier="stylua",
        manager=Brew,
        description="Opinionated Lua code formatter",
    ),
    Package(
        identifier="taplo",
        manager=Brew,
        description="TOML toolkit written in Rust",
    ),
    Package(
        identifier="telegram",
        manager=Brew,
        description="Messaging app with a focus on speed and security",
    ),
    Package(
        identifier="tree",
        manager=Brew,
        description="Display directories as trees (with optional color/HTML output)",
    ),
    Package(
        name="Visual Studio Code",
        identifier="visual-studio-code",
        manager=Brew,
        description="GUI code editor developed by Microsoft",
    ),
    Package(
        identifier="yazi",
        manager=Brew,
        description="Blazing fast terminal file manager written in Rust, based on async I/O",
    ),
    Package(
        identifier="yt-dlp",
        manager=Brew,
        description="Feature-rich command-line audio/video downloader",
    ),
    Package(
        identifier="zip",
        manager=Brew,
        description="Compression and file packaging/archive utility",
    ),
    Package(
        identifier="zsh-fast-syntax-highlighting?",
        manager=Brew,
        description="Feature-rich syntax highlighting for Zsh",
        condition=os.environ["SHELL"] == "/bin/zsh",
    ),
    Package(identifier="dunst", manager=Yay),
    Package(identifier="gruvbox-dark-gtk", manager=Yay),
    Package(identifier="maim", manager=Yay),
    Package(identifier="pamixer", manager=Yay),
    Package(identifier="pulsemixer", manager=Yay),
    Package(identifier="taskwarrior-tui", manager=Yay),
    Package(identifier="trash-cli", manager=Yay),
    Package(identifier="ueberzugpp", manager=Yay),
    Package(
        identifier="unzip",
        manager=Yay,
        description="Extraction utility for .zip compressed archives",
    ),
    Package(identifier="xcompmgr", manager=Yay),
    Package(identifier="xdotool", manager=Yay),
    Package(identifier="xorg-server", manager=Yay),
    Package(identifier="xorg-xev", manager=Yay),
    Package(identifier="xorg-xinit", manager=Yay),
    Package(identifier="xwallpaper", manager=Yay),
    Package(identifier="zathura-pdf-poppler", manager=Yay),
]
