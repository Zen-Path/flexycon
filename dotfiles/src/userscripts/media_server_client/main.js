// ==UserScript==
// @name            File Downloader
// @namespace       Flexycon
// @match           http*://*/*
// @version         2.0.3
// @author          Zen-Path
// @description     Send a download request for a URL to a local media server
// @downloadURL
// @supportURL      https://github.com/Zen-Path/flexycon/tree/main/dotfiles/src/scripts/media_server
// @homepageURL     https://github.com/Zen-Path/flexycon
// @icon            https://www.svgrepo.com/show/230395/download.svg
// @grant           GM_registerMenuCommand
// @grant           GM_xmlhttpRequest
// @grant           GM_openInTab
// @grant           GM_addStyle
// @grant           GM_addElement
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
            alert("Download successful!");
        },
    });
}

const STYLES = `
{%@@ include 'src/userscripts/media_server_client/style.css' @@%}
`;

function createDownloadForm() {
    // {%@@ include 'src/userscripts/media_server_client/createDownloadForm.js' @@%}
}

function main() {
    GM_registerMenuCommand("Download Media", () => {
        const currentUrl = window.location.href;
        downloadMedia([currentUrl], MEDIA_TYPES.UNKNOWN);
    });

    GM_registerMenuCommand("Open Download Form", async () => {
        const formData = await createDownloadForm();
        console.log("Download Form Data:", formData);

        if (!formData) return;

        downloadMedia(
            formData.urls,
            formData.mediaType,
            formData.range === ":" ? null : formData.range
        );
    });

    GM_registerMenuCommand("Open Dashboard", () => {
        // { active: true } ensures the new tab gets focus immediately
        GM_openInTab(`${BASE_URL}/dashboard`, { active: true });
    });
}

main();
