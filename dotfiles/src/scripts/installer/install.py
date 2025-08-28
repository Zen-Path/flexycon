from collections import defaultdict

from scripts.installer.packages import Package, PacMan, Yay

install_packages = [
    Package(
        id="git",
        manager=Yay,
        description="a distributed version control system",
        tags=["terminal"],
    ),
    Package(
        id="alacritty",
        manager=Yay,
        description="a cross-platform, GPU-accelerated terminal emulator",
        tags=["terminal"],
    ),
    Package(
        id="firefox",
        manager=PacMan,
        description="a private & safe web browser",
        tags=["gui"],
    ),
    Package(
        id="fzf",
        manager=Yay,
        description="a fuzzy finder in the terminal",
        tags=["terminal"],
    ),
]

# Unix
# bat
# bottom
# vscode
# clang
# mpv
# newsraft
# taskwarrior-tui
# unrar
# zip
# unzip
# yazi
# zsh-fast-syntax-highlighting-git
# fd
# dust
# taplo
# tree
# ripgrep
# ripgrep-all
# 7zip
# rclone
# npm
# node

# X11
# dunst
# maim
# pamixer
# pulsemixer
# ueberzugpp
# xcompmgr
# xdotool
# xorg-server
# xorg-xev
# xorg-xinit
# xwallpaper
# gruvbox-dark-gtk
# trash-cli
# zathura-pdf-poppler


if __name__ == "__main__":
    grouped = defaultdict(list)
    for pkg in install_packages:
        grouped[pkg.manager].append(pkg)

    for manager, pkg_list in grouped.items():
        print(f"Installing packages using {manager.__name__}:")
        manager.install(list(map(lambda p: p.id, pkg_list)))

    # for package in install_packages:
    # package.manager.install(package.id)
