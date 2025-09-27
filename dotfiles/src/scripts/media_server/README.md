# Media Server

A script that handles download requests for URLs.

## Installation

1. Install the `ViolentMonkey` extension (guide [here](https://violentmonkey.github.io/get-it/))
2. Add the [client script](./js/client.js) to ViolentMonkey (guide [here](https://violentmonkey.github.io/guide/creating-a-userscript/))
3. (Optional) Set up the environmental variables:

    Copy `example.env` to `.env` in `src/`. Paths should be absolute.

## Usage

To launch the app:

```sh
cd $FLEXYCON_HOME
source venv/bin/activate
media_server --verb
```

## Tips

### DownThemAll

The [DownThemAll](https://www.downthemall.org/) extension provides an easy way to download files with a structured filename, and in bulk.

I found this mask pretty useful:

```
*y*-*m*-*d*-*hh*-*mm*-*ss*_*flathost*_*flatname*.*ext*
```
