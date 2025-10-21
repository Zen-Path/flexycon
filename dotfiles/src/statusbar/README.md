# General

## Limitations

The current approach to deploy python scripts without needing a wrapper is to
add flexycon's venv path to the shebang using dotdrop's templating. This isn't
ideal, however it works for now. One limitation is that to call any binary
installed in the venv from a script, we have to provide the full path
to the binary.
