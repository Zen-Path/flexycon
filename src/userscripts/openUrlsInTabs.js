// ==UserScript==
// @name         Open URLs in Tabs
// @namespace    Flexycon
// @version      0.0.6
// @author       Zen-Path
// @description  Open a given list of URLs in new tabs.
// @homepageURL  https://github.com/Zen-Path/flexycon
// @match        *://*/*
// @grant        GM_openInTab
// @grant        GM_registerMenuCommand
// @noframes
// ==/UserScript==

function main() {
    "use strict";

    GM_registerMenuCommand("Insert URLs", () => {
        const linksRaw = prompt("Insert URLs");
        if (linksRaw === null) return;

        const validLinks = linksRaw.split(" ").flatMap((link) => {
            const trimmed = link.trim();
            if (!trimmed) return []; // Skip empty strings

            try {
                // This will throw an error if not a valid absolute URL
                const urlObj = new URL(trimmed);
                return [urlObj.href];
            } catch (e) {
                console.warn(`Invalid URL: '${trimmed}'`);
                return [];
            }
        });

        // Open the links
        validLinks.reverse().forEach((link) => {
            GM_openInTab(link, { active: false });
        });
    });
}

main();
