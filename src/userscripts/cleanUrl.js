// ==UserScript==
// @name         Clean URLs
// @namespace    Flexycon
// @version      0.0.9
// @author       Zen-Path
// @description  Clean up the URL so it can be easily shared or stored.
// @homepageURL  https://github.com/Zen-Path/flexycon
// @match        *://*/*
// @grant        GM_registerMenuCommand
// @noframes
// ==/UserScript==

function cleanTemu(url) {
    if (url.pathname === "/goods.html") {
        const targetParam = "goods_id";
        const goodsId = url.searchParams.get(targetParam);
        if (!goodsId) {
            log.warn("Could not find a product ID (goods_id) in this URL.");
            return false;
        }

        url.search = "";
        url.searchParams.set(targetParam, goodsId);

        return true;
    } else if (url.pathname === "/mall.html") {
        const targetParam = "mall_id";
        const mall_id = url.searchParams.get(targetParam);
        if (!mall_id) {
            log.warn("Could not find a seller ID (mall_id) in this URL.");
            return false;
        }

        url.search = "";
        url.searchParams.set(targetParam, mall_id);

        return true;
    }

    return false;
}

function cleanYoutube(url) {
    // Strip /featured from the channel page
    if (url.pathname.startsWith("/@")) {
        if (/\/featured\/?$/.test(url.pathname)) {
            url.pathname = url.pathname.replace(/\/featured\/?$/, "");
            return true;
        }
    } else if (url.pathname === "/watch") {
        const targetParam = "v";
        const video_id = url.searchParams.get(targetParam);
        if (!video_id) {
            log.warn("Could not find a seller ID (mall_id) in this URL.");
            return false;
        }

        url.search = "";
        url.searchParams.set(targetParam, video_id);

        return true;
    }

    return false;
}

function cleanImdb(url) {
    ["ref_", "ref"].forEach((param) => {
        url.searchParams.delete(param);
    });

    return true;
}

const CLEANER_REGISTRY = {
    "temu.com": cleanTemu,
    "youtube.com": cleanYoutube,
    "imdb.com": cleanImdb,
};

function main() {
    "use strict";

    const currentHostname = location.hostname;

    // Is it a known hostname?
    const registryKey = Object.keys(CLEANER_REGISTRY).find((key) =>
        currentHostname.includes(key)
    );
    if (!registryKey) return;

    GM_registerMenuCommand("Clean Url", () => {
        const url = new URL(location.href);
        const handler = CLEANER_REGISTRY[registryKey];

        const isCleaned = handler(url);

        if (isCleaned) {
            window.history.replaceState({}, "", url.toString());
        } else {
            alert(
                "This URL could not be cleaned. Check the console for more info."
            );
        }
    });
}

main();
