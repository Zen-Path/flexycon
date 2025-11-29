// ==UserScript==
// @name            File Downloader
// @namespace       Flexycon
// @match           http*://*/*
// @version         1.5.3
// @author          Zen-Path
// @description     Send a download request for a URL to a local media server
// @downloadURL
// @supportURL      https://github.com/Zen-Path/flexycon/tree/main/dotfiles/src/scripts/media_server
// @homepageURL     https://github.com/Zen-Path/flexycon
// @icon            https://www.svgrepo.com/show/230395/download.svg
// @grant           GM_registerMenuCommand
// @grant           GM_xmlhttpRequest
// @noframes
// ==/UserScript==

"use strict";

const SERVER_PORT = "{{@@ _vars['media_server_port'] @@}}";
const BASE_URL = `http://localhost:${SERVER_PORT}`;

const MEDIA_TYPES = {
    IMAGE: "image",
    VIDEO: "video",
    GALLERY: "gallery",
    UNKNOWN: "unknown",
};

const DOWNLOAD_FAILURE_PATTERNS = [
    "[ytdl][error]",
    "[downloader.http][warning] File size larger",
];

function downloadMedia(urls, mediaType, range) {
    const payload = { urls, media_type: mediaType };
    if (range !== undefined) {
        payload.range = range;
    }
    const requestData = JSON.stringify(payload);

    GM_xmlhttpRequest({
        method: "POST",
        url: `${BASE_URL}/media/download`,
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": "{{@@ _vars['media_server_key'] @@}}",
        },
        data: requestData,
        onerror: function (error) {
            console.error(":: Download failed", error);
            alert("Download failed.");
        },
        onload: function (response) {
            console.log(":: Response info", response);

            // TODO: Improve error handling
            // if (response.status !== 200) {
            //     alert(
            //         `Download failed. Response status is ${response.status}.`
            //     );
            //     return;
            // }

            // const data = JSON.parse(response.responseText);

            // if (data.return_code !== 0) {
            //     alert(`Download failed. Return code is ${data.return_code}.`);
            //     return;
            // }

            // const output_fmt = data.output.trim();

            // console.log(
            //     ":: Download info",
            //     `
            // - request_status: ${response.status}
            // - process_return_code: ${data.return_code}
            // - output:\n${output_fmt}`
            // );

            // if (
            //     !DOWNLOAD_FAILURE_PATTERNS.every(
            //         (pattern) => !output_fmt.includes(pattern)
            //     )
            // ) {
            //     alert("Download failed. Output includes error.");
            //     return;
            // }

            alert("Download successful!");
        },
    });
}

function main() {
    GM_registerMenuCommand("Download Media", () => {
        const currentUrl = window.location.href;
        downloadMedia([currentUrl], MEDIA_TYPES.UNKNOWN);
    });

    GM_registerMenuCommand("Download (Specify Type)", () => {
        const currentUrl = window.location.href;
        const mediaType = prompt(
            `Insert media type. Must be one of ${Object.values(MEDIA_TYPES).join(", ")}`
        );
        if (Object.values(MEDIA_TYPES).includes(mediaType)) {
            downloadMedia([currentUrl], MEDIA_TYPES.UNKNOWN);
        } else {
            alert(`Error: Unknown media type: ${mediaType}.`);
        }
    });

    GM_registerMenuCommand("Download Gallery Range", () => {
        const currentUrl = window.location.href;
        const range = prompt("Type the range (start:end).");
        downloadMedia([currentUrl], MEDIA_TYPES.GALLERY, range);
    });

    GM_registerMenuCommand("Download Galleries", () => {
        const userInput = prompt("Paste the gallery urls.");
        const galleryUrls = userInput.split(" ");
        downloadMedia(galleryUrls, MEDIA_TYPES.GALLERY);
    });
}

main();
