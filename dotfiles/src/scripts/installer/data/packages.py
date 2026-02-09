import os

from common.helpers import get_display_server
from common.packages.package_managers import Brew, Git, Package, Yay

display_server = get_display_server()

packages = [
    Package(
        identifier="alacritty",
        managers=[Yay],
        description="A cross-platform, GPU-accelerated terminal emulator",
    ),
    Package(
        identifier="bat",
        managers=[Brew, Yay],
        description="cat(1) clone with syntax highlighting and Git integration",
    ),
    Package(
        identifier="bottom",
        managers=[Brew, Yay],
        description="Yet another cross-platform graphical process/system monitor",
    ),
    Package(
        identifier="dust",
        managers=[Brew, Yay],
        description="More intuitive version of du in rust",
    ),
    Package(
        identifier="exiftool",
        managers=[Brew, Yay],
        description="Perl lib for reading and writing EXIF metadata",
    ),
    Package(
        identifier="fd",
        managers=[Brew, Yay],
        description="Simple, fast and user-friendly alternative to find",
    ),
    Package(
        identifier="ffmpeg",
        managers=[Brew, Yay],
        description="Play, record, convert, and stream audio and video",
    ),
    Package(
        identifier="firefox",
        managers=[Brew, Yay],
        is_gui=True,
        description="Free and open source web browser",
    ),
    Package(
        identifier="fzf",
        managers=[Brew, Yay],
        description="Fuzzy finder in the terminal",
    ),
    Package(
        identifier="ghostscript",
        managers=[Brew, Yay],
        description="Interpreter for PostScript and PDF",
    ),
    Package(
        identifier="git",
        managers=[Brew, Yay],
        description="Distributed revision control system",
    ),
    Package(
        identifier="imagemagick",
        managers=[Brew, Yay],
        description="Tools and libraries to manipulate images in many formats",
    ),
    Package(
        identifier="jq",
        managers=[Brew, Yay],
        description="Command-line JSON processor",
    ),
    Package(
        identifier="kitty",
        managers=[Brew],
        is_gui=True,
        description="GPU-based terminal emulator",
    ),
    Package(
        identifier="mpv",
        managers=[Brew, Yay],
        description="Media player based on MPlayer and mplayer2",
    ),
    Package(
        name="NeoVim",
        identifier="neovim",
        managers=[Brew, Yay],
        description="Ambitious Vim-fork focused on extensibility and agility",
    ),
    Package(
        identifier="newsraft",
        managers=[Brew, Yay],
        description="Terminal feed reader",
    ),
    Package(
        identifier="node",
        managers=[Brew, Yay],
        description="JS platform built on V8 to build network applications",
    ),
    Package(
        identifier="prettier",
        managers=[Brew, Yay],
        description="Code formatter for JavaScript, CSS, JSON, GraphQL, Markdown, YAML",
    ),
    Package(
        identifier="rclone",
        managers=[Brew, Yay],
        description="Rsync for cloud storage",
    ),
    Package(
        identifier="ripgrep",
        managers=[Brew, Yay],
        description="Search tool like grep and The Silver Searcher",
    ),
    Package(
        identifier="ripgrep-all",
        managers=[Brew, Yay],
        description="Wrapper around ripgrep that adds multiple rich file types",
    ),
    Package(
        identifier="shfmt",
        managers=[Brew, Yay],
        description="Autoformat shell script source code",
    ),
    Package(
        identifier="sqlite",
        managers=[Brew, Yay],
        description="Command-line interface for SQLite",
    ),
    Package(
        identifier="starship",
        managers=[Brew, Yay],
        description="Cross-shell prompt for astronauts",
    ),
    Package(
        identifier="stylua",
        managers=[Brew, Yay],
        description="Opinionated Lua code formatter",
    ),
    Package(
        identifier="taplo",
        managers=[Brew, Yay],
        description="TOML toolkit written in Rust",
    ),
    Package(
        identifier="telegram",
        # TODO: Installing telegram through the website results in Telegram Desktop,
        # which has more features than Telegram for Mac
        managers=[],
        is_gui=True,
        description="Messaging app with a focus on speed and security",
    ),
    Package(
        identifier="tree",
        managers=[Brew, Yay],
        description="Display directories as trees (with optional color/HTML output)",
    ),
    # TODO: implement per-manager identifiers
    Package(
        name="Visual Studio Code",
        identifier="visual-studio-code",
        managers=[Brew],
        is_gui=True,
        description="GUI code editor developed by Microsoft",
    ),
    Package(
        name="Visual Studio Code Linux",
        identifier="code",
        managers=[Yay],
        is_gui=True,
        description="GUI code editor developed by Microsoft",
    ),
    Package(
        identifier="yazi",
        managers=[Brew, Yay],
        description="Blazing fast terminal file manager written in Rust, based on async I/O",
    ),
    Package(
        identifier="yt-dlp",
        managers=[Brew, Yay],
        description="Feature-rich command-line audio/video downloader",
    ),
    Package(
        identifier="zip",
        managers=[Brew, Yay],
        description="Compression and file packaging/archive utility",
    ),
    Package(
        name="Zsh Fast Syntax Highlighting",
        identifier="zsh-syntax-highlighting",
        managers=[Brew],
        description="Feature-rich syntax highlighting for Zsh",
        condition=os.environ["SHELL"] == "/bin/zsh",
    ),
    Package(
        name="Zsh Fast Syntax Highlighting Linux",
        identifier="zsh-fast-syntax-highlighting-git",
        managers=[Yay],
        description="Feature-rich syntax highlighting for Zsh",
        condition=os.environ["SHELL"] == "/usr/bin/zsh",
    ),
    Package(
        identifier="dunst",
        managers=[Yay],
        description="A highly configurable and lightweight notification daemon",
    ),
    Package(
        identifier="gruvbox-dark-gtk",
        managers=[Yay],
        description="A gruvbox dark theme. Supports GTK 2.0 and 3.0",
    ),
    Package(
        identifier="maim",
        managers=[Yay],
        description="maim (make image) makes an image out of the given area on the given X screen. Defaults to the whole screen",
    ),
    Package(
        identifier="pamixer",
        managers=[Yay],
        description="Pulseaudio command-line mixer like amixer",
    ),
    Package(
        identifier="pulsemixer",
        managers=[Yay],
        description="cli and curses mixer for pulseaudio",
    ),
    Package(
        identifier="taskwarrior-tui",
        managers=[Yay],
        description="a terminal user interface for taskwarrior",
    ),
    Package(
        identifier="trash-cli",
        managers=[Yay],
        description="a cli system trash manager, alternative to rm and trash-cli",
    ),
    Package(
        identifier="ueberzugpp",
        managers=[Yay],
        description="Display images in the terminal (drop-in replacement for ueberzug written in C++)",
    ),
    Package(
        identifier="unzip",
        managers=[Yay],
        description="Extraction utility for .zip compressed archives",
    ),
    Package(
        identifier="xcompmgr",
        managers=[Yay],
        description="The X Compositing Manager fresh from freedesktop.org repositories",
        condition=display_server == "X11",
    ),
    Package(
        identifier="xdotool",
        managers=[Yay],
        description="Command-line X11 automation tool",
        condition=display_server == "X11",
    ),
    Package(
        identifier="xorg-server",
        managers=[Yay],
        description="Xorg X server",
        condition=display_server == "X11",
    ),
    Package(
        identifier="xorg-xev",
        managers=[Yay],
        description="Catch X11 events and print them",
        condition=display_server == "X11",
    ),
    Package(
        identifier="xorg-xinit",
        managers=[Yay],
        description="X.Org initialization program",
        condition=display_server == "X11",
    ),
    Package(
        identifier="xwallpaper",
        managers=[Yay],
        description="Wallpaper setting utility for X",
        condition=display_server == "X11",
    ),
    Package(
        identifier="zathura-pdf-poppler",
        managers=[Yay],
        description="PDF support for zathura (poppler backend)",
    ),
    Package(
        identifier="https://github.com/Zen-Path/flexycon-private",
        managers=[Git],
        destination=["$XDG_SRC_HOME", "flexycon-private"],
        description="Private config",
    ),
    Package(
        identifier="https://github.com/Zen-Path/media-server",
        managers=[Git],
        destination=["$XDG_SRC_HOME", "media-server"],
        description="Local media server to download and manage files",
    ),
    Package(
        identifier="https://github.com/Zen-Path/dwm-flexipatch",
        managers=[Git],
        destination=["$XDG_SRC_HOME", "dwm-flexipatch"],
        description="A dwm build with preprocessor directives to decide which patches to include during build time.",
        condition=display_server == "X11",
    ),
    Package(
        identifier="https://github.com/Zen-Path/dwmblocks-async",
        managers=[Git],
        destination=["$XDG_SRC_HOME", "dwmblocks-async"],
        description="An efficient, lean, and asynchronous status feed generator for dwm.",
        condition=display_server == "X11",
    ),
    Package(
        identifier="https://github.com/Zen-Path/dmenu-flexipatch",
        managers=[Git],
        destination=["$XDG_SRC_HOME", "dmenu-flexipatch"],
        description="A dmenu build with preprocessor directives to decide which patches to include during build time.",
        condition=display_server == "X11",
    ),
    Package(
        identifier="https://github.com/Zen-Path/slock-flexipatch",
        managers=[Git],
        destination=["$XDG_SRC_HOME", "slock-flexipatch"],
        description="An slock build with preprocessor directives to decide which patches to include during build time.",
        condition=display_server == "X11",
    ),
    Package(
        identifier="https://github.com/Zen-Path/nsxiv",
        managers=[Git],
        destination=["$XDG_SRC_HOME", "nsxiv"],
        description="Neo Simple X Image Viewer https://nsxiv.codeberg.page.",
        condition=display_server == "X11",
    ),
    Package(
        identifier="https://github.com/Zen-Path/nsxiv-extra",
        managers=[Git],
        destination=["$XDG_SRC_HOME", "nsxiv-extra"],
        description="Community patches, scripts, tips and tricks for nsxiv.",
        condition=display_server == "X11",
    ),
]
