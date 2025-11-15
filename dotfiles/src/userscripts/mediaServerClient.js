// ==UserScript==
// @name            File Downloader
// @namespace       Flexycon
// @match           http*://*/*
// @version         1.4.5
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

const SERVER_PORT = "{{@@ _vars['media_server_port'] @@}}";

const DOWNLOAD_FAILURE_PATTERNS = [
    "[ytdl][error]",
    "[downloader.http][warning] File size larger",
];

function downloadMedia(urls, type, range) {
    const payload = { urls, type };
    if (range !== undefined) {
        payload.range = range;
    }
    const requestData = JSON.stringify(payload);

    GM_xmlhttpRequest({
        method: "POST",
        url: `http://localhost:${SERVER_PORT}/media/download`,
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

            if (response.status !== 200) {
                alert(
                    `Download failed. Response status is ${response.status}.`
                );
                return;
            }

            const data = JSON.parse(response.responseText);

            if (data.return_code !== 0) {
                alert(`Download failed. Return code is ${data.return_code}.`);
                return;
            }

            const output_fmt = data.output.trim();

            console.log(
                ":: Download info",
                `
- request_status: ${response.status}
- process_return_code: ${data.return_code}
- output:\n${output_fmt}`
            );

            if (
                !DOWNLOAD_FAILURE_PATTERNS.every(
                    (pattern) => !output_fmt.includes(pattern)
                )
            ) {
                alert("Download failed. Output includes error.");
                return;
            }

            alert("Download successful!");
        },
    });
}

function main() {
    GM_registerMenuCommand("Download Gallery", () => {
        const currentUrl = window.location.href;
        downloadMedia([currentUrl], "gallery");
    });

    GM_registerMenuCommand("Download Gallery Range", () => {
        const range = prompt("Type the range (start:end).");
        const currentUrl = window.location.href;
        downloadMedia([currentUrl], "gallery", range);
    });

    GM_registerMenuCommand("Download Galleries", () => {
        const userInput = prompt("Paste the gallery urls.");
        const galleryUrls = userInput.split(" ");
        downloadMedia(galleryUrls, "gallery");
    });
}

main();
