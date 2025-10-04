# Firefox

- [Firefox](#firefox)
    - [Extensions](#extensions)
        - [DownThemAll](#downthemall)

## Extensions

| Name                   | Description                                                                                                                   | Link                                                                                            |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| uBlock Origin          | Finally, an efficient blocker. Easy on CPU and memory                                                                         | [link](https://addons.mozilla.org/en-US/firefox/addon/uBlock0@raymondhill.net)                  |
| Bitwarden              | At home, at work, or on the go, Bitwarden easily secures all your passwords, passkeys, and sensitive information              | [link](https://addons.mozilla.org/en-US/firefox/addon/{446900e4-71c2-419f-a6a7-df9c091e268b})   |
| Dark Reader            | Dark mode for every website. Take care of your eyes, use dark theme for night and daily browsing                              | [link](https://addons.mozilla.org/en-US/firefox/addon/addon@darkreader.org)                     |
| Violentmonkey          | An open source userscript manager that supports a lot of browsers                                                             | [link](https://addons.mozilla.org/en-US/firefox/addon/{aecec67f-0d10-4fa7-b7c7-609a2db280cf})   |
| DownThemAll!           | The Mass Downloader for your browser                                                                                          | [link](https://addons.mozilla.org/en-US/firefox/addon/{DDC359D1-844A-42a7-9AA1-88A850A938A8})   |
| Search by Image        | A powerful reverse image search tool, with support for various search engines, such as Google, Bing, Yandex, Baidu and TinEye | [link](https://addons.mozilla.org/en-US/firefox/addon/{2e5ff8c8-32fe-46d0-9fc8-6b8986621f3c})   |
| find+                  | A find-in-page extension for Google Chrome with support for regular expressions                                               | [link](https://addons.mozilla.org/en-US/firefox/addon/{6fa42eda-38ca-4126-96d5-3163f0de6900})   |
| Vimium                 | The Hacker's Browser. Vimium provides keyboard shortcuts for navigation and control in the spirit of Vim                      | [link](https://addons.mozilla.org/en-US/firefox/addon/{d7742d87-e61d-4b78-b8a1-b469842139fa})   |
| Export Tabs URLs       | Save a list of all open tabs into a text file or the clipboard                                                                | [link](https://addons.mozilla.org/en-US/firefox/addon/{17165bd9-9b71-4323-99a5-3d4ce49f3d75})   |
| Sort Tabs by URL       | Sorts the tabs alphabetically A-Z or Z-A                                                                                      | [link](https://addons.mozilla.org/en-US/firefox/addon/jid0-uRZpLu7VtYEF3IY7A2TpX21yj3A@jetpack) |
| Bookmark Dupes         | Display/Remove duplicate bookmarks, empty folders, or descriptions                                                            | [link](https://addons.mozilla.org/en-US/firefox/addon/bookmarkdupes@martin-vaeth.org)           |
| Unhook - YouTube       | Hide YouTube related videos, shorts, comments, suggestions wall, homepage recommendations, trending, and other distractions   | [link](https://addons.mozilla.org/en-US/firefox/addon/myallychou@gmail.com)                     |
| SponsorBlock - YouTube | Skip sponsorships, subscription begging and more on YouTube videos. Report sponsors on videos you watch to save others' time  | [link](https://addons.mozilla.org/en-US/firefox/addon/sponsorBlocker@ajay.app)                  |

This table above was created from my Firefox profile’s `extensions.json` file and the output of this command:

```py
import json, os, sys

extensions_path, = sys.argv[1:]
path = os.path.join(extensions_path)
data = json.load(open(path, encoding='utf-8'))

for addon in data['addons']:
    # enabled = '*' if addon['active'] else ' '
    name = addon['defaultLocale']['name'].replace("|", "-")
    description = addon['defaultLocale'].get('description', "").replace("|", "-").rstrip(".")
    id = f"[link](https://addons.mozilla.org/en-US/firefox/addon/{addon["id"]})"

    print("|", " | ".join([name, description, id]), "|")
```

### DownThemAll

I found this mask pretty useful:

```
*y*-*m*-*d*-*hh*-*mm*-*ss*_*flathost*_*flatname*.*ext*
```
