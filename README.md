# flexycon

Flexible programmatic configuration.

## Tips

### Monday as first day of the week

1. Open `/etc/locale.conf`
2. Change `LC_TIME` to `en_DK.UTF-8` (Denmark)
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
