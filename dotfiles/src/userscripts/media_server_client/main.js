// ==UserScript==
// @name            File Downloader
// @namespace       Flexycon
// @match           http*://*/*
// @version         2.0.15
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

// prettier-ignore
const DOWNLOAD_STATUS = Object.freeze({
    PENDING:        0,
    IN_PROGRESS:    1,
    DONE:           2,
    FAILED:         3,
    MIXED:          4,
});

// prettier-ignore
const STATUS_ICONS = Object.freeze({
    [DOWNLOAD_STATUS.PENDING]:      "🔜",
    [DOWNLOAD_STATUS.IN_PROGRESS]:  "⏳",
    [DOWNLOAD_STATUS.DONE]:         "🟩",
    [DOWNLOAD_STATUS.FAILED]:       "🟥",
    [DOWNLOAD_STATUS.MIXED]:        "🟨",
})

/**
 * Updates the document title with a status icon.
 * Pass a value from DOWNLOAD_STATUS to add/change an icon.
 * Pass null to remove any existing status icons.
 */
function showDownloadStatus(statusId) {
    const icon = STATUS_ICONS[statusId];
    if (icon && document.title.startsWith(`${icon} - `)) {
        return;
    }

    const allIcons = Object.values(STATUS_ICONS).join("");
    const statusRegex = new RegExp(`^[${allIcons}]\\s-\\s`, "u");
    const cleanTitle = document.title.replace(statusRegex, "");

    document.title = icon ? `${icon} - ${cleanTitle}` : cleanTitle;
}

function downloadMedia(urls, mediaType, rangeStart, rangeEnd) {
    showDownloadStatus(DOWNLOAD_STATUS.IN_PROGRESS);

    const payload = { urls, mediaType };
    if (Number.isInteger(startVal)) {
        payload.rangeStart = startVal;
    }
    if (Number.isInteger(endVal)) {
        payload.rangeEnd = endVal;
    }

    const requestData = JSON.stringify(payload);

    GM_xmlhttpRequest({
        method: "POST",
        url: `${BASE_URL}/api/media/download`,
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": "{{@@ _vars['media_server_key'] @@}}",
        },
        data: requestData,
        onerror: function (error) {
            console.error(":: Download failed", error);
            showDownloadStatus(DOWNLOAD_STATUS.ERROR);
        },
        onload: function (response) {
            console.log(":: Response info", response);

            // TODO: Improve error handling

            showDownloadStatus(DOWNLOAD_STATUS.SUCCESS);
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
            formData.rangeStart,
            formData.rangeEnd
        );
    });

    GM_registerMenuCommand("Open Dashboard", () => {
        // { active: true } ensures the new tab gets focus immediately
        GM_openInTab(`${BASE_URL}/dashboard`, { active: true });
    });
}

main();
