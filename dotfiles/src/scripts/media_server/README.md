# Media Server

A script that handles download requests for URLs.

- [Media Server](#media-server)
    - [Dependencies](#dependencies)
    - [Installation](#installation)
    - [Usage](#usage)

## Dependencies

- `gallery-dl` - for image downloads
- `yt-dlp` - for video downloads and gallery-dl fallback

If configured, `gallery-dl` can use `yt-dlp` as a fallback, so it needs to be installed system-wide, not in the venv.

## Installation

1. Install the `ViolentMonkey` extension (guide [here](https://violentmonkey.github.io/get-it/))
2. Add the [client script](./../../userscripts/mediaServerClient.js) to ViolentMonkey (guide [here](https://violentmonkey.github.io/guide/creating-a-userscript/))
3. (Optional) Set up the environmental variables:

    Copy `example.env` to `.env` in `src/`. Paths should be absolute.

## Usage

To launch the app:

```sh
cd $FLEXYCON_HOME
source venv/bin/activate
media_server --verb
```
