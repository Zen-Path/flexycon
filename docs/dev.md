# Development

- [Development](#development)
    - [dotdrop](#dotdrop)
    - [Installing scripts](#installing-scripts)

## dotdrop

Use this to quickly see the template dotfile variables.

```
# dotdrop_dotpath {{@@ _dotdrop_dotpath @@}}
# dotdrop_cfgpath {{@@ _dotdrop_cfgpath @@}}
# dotdrop_workdir {{@@ _dotdrop_workdir @@}}

# dotfile_abs_src {{@@ _dotfile_abs_src @@}}
# dotfile_abs_dst {{@@ _dotfile_abs_dst @@}}

# dotfile_key  {{@@ _dotfile_key @@}}
# dotfile_link {{@@ _dotfile_link @@}}

# dotfile_sub_abs_src {{@@ _dotfile_sub_abs_src @@}}
# dotfile_sub_abs_dst {{@@ _dotfile_sub_abs_dst @@}}
```

## Installing scripts

The current approach to installing python scripts is to add flexycon's venv path to the shebang using
dotdrop's templating.

One limitation is that to call any binary installed in the venv from a script,
we have to provide the full path to the binary. This means that, for example,
to call dotdrop, we have to use `/path/to/flexycon/.venv/bin/dotdrop` instead
of just `dotdrop`.
