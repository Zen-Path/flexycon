// ==UserScript==
// @name            File Downloader
// @namespace       Flexycon
// @match           http*://*/*
// @version         2.2.0
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

const API_DOWNLOAD = `${BASE_URL}/api/media/download`;

// Mirror of the backend MediaType Enum
// prettier-ignore
const MediaType = Object.freeze({
    GALLERY:    0,
    IMAGE:      1,
    VIDEO:      2,
    AUDIO:      3,
    TEXT:       4,
});

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

let statusFlashTimer = null;

/**
 * Updates the document title with a status icon and optional flashing effect.
 * @param {number} statusId - The ID from DOWNLOAD_STATUS
 * @param {boolean} [flash=false] - If true, the icon will flash to grab attention
 * - After a short timer, the icon remains static.
 */
function showDownloadStatus(statusId, flash = true) {
    // Clear existing flashers
    if (statusFlashTimer) {
        clearInterval(statusFlashTimer);
        statusFlashTimer = null;
    }

    const icon = STATUS_ICONS[statusId];
    if (icon && document.title.startsWith(`${icon} - `)) {
        return;
    }

    const allIcons = Object.values(STATUS_ICONS).join("");
    const statusRegex = new RegExp(`^[${allIcons}]\\s-\\s`, "u");
    const cleanTitle = document.title.replace(statusRegex, "");

    if (!icon) {
        document.title = cleanTitle;
        return;
    }

    const staticTitle = `${icon} - ${cleanTitle}`;
    if (!flash) {
        document.title = staticTitle;
        return;
    }

    // Start flashing
    let showIcon = true;
    statusFlashTimer = setInterval(() => {
        document.title = showIcon ? staticTitle : cleanTitle;
        showIcon = !showIcon;
    }, 500);

    // Auto-stop flashing
    setTimeout(() => {
        if (statusFlashTimer) {
            clearInterval(statusFlashTimer);
            statusFlashTimer = null;
            document.title = staticTitle;
        }
    }, 3000);
}

function downloadMedia(urls, mediaType, rangeStart, rangeEnd) {
    showDownloadStatus(DOWNLOAD_STATUS.IN_PROGRESS, false);

    const payload = { urls, mediaType };
    if (Number.isInteger(rangeStart)) {
        payload.rangeStart = rangeStart;
    }
    if (Number.isInteger(rangeEnd)) {
        payload.rangeEnd = rangeEnd;
    }

    const requestData = JSON.stringify(payload);

    GM_xmlhttpRequest({
        method: "POST",
        url: API_DOWNLOAD,
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": "{{@@ _vars['media_server_key'] @@}}",
        },
        data: requestData,
        onload: function (response) {
            if (response.status < 200 || response.status > 300) {
                console.warn(":: Response info", response);
                showDownloadStatus(DOWNLOAD_STATUS.FAILED);
                return;
            }

            try {
                const report = JSON.parse(response.responseText);
                const entries = Object.entries(report);
                console.log(":: Download response", report);

                if (entries.length === 0) {
                    console.error("Empty response from server");
                    showDownloadStatus(DOWNLOAD_STATUS.FAILED);
                    return;
                }

                const totalItems = entries.length;
                const successCount = entries.filter(
                    ([_, data]) => data.status === true
                ).length;

                let overallStatus;
                if (successCount === totalItems) {
                    overallStatus = DOWNLOAD_STATUS.DONE;
                } else if (successCount === 0) {
                    overallStatus = DOWNLOAD_STATUS.FAILED;
                } else {
                    overallStatus = DOWNLOAD_STATUS.MIXED;
                }

                showDownloadStatus(overallStatus);

                // Log failures for debugging
                if (successCount < totalItems) {
                    entries.forEach(([url, data]) => {
                        if (!data.status) {
                            console.error(
                                `Error for ${url}:`,
                                data.error || "Unknown error"
                            );
                        }
                    });
                }
            } catch (error) {
                console.error("Failed to parse server response", error);
                showDownloadStatus(DOWNLOAD_STATUS.FAILED);
            }
        },
        onerror: function (error) {
            console.error("Download failed", error);
            showDownloadStatus(DOWNLOAD_STATUS.FAILED);
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
        downloadMedia([currentUrl], null);
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
