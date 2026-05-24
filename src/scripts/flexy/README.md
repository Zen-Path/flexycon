# Flexy

Manage flexycon dotfiles and some system configs.

- [Flexy](#flexy)
    - [Dev](#dev)

## Dev

`flexy` is not managed by dotdrop because it is fundamentally linked to this repo
and dotfile changes would not be properly installed if the installer itself is
compromised. For example, if any of the imports is renamed, then python will throw an
error, since the version of flexy that is installed in `XDG_LOCAL_BIN` expects a
different import name
