// ==UserScript==
// @name            File Downloader
// @namespace       Flexycon
// @match           http*://*/*
// @version         1.4.3
// @author          Zen-Path
// @description     Send a download request for a URL to a local media server
// @downloadURL     https://raw.githubusercontent.com/Zen-Path/flexycon/refs/heads/main/dotfiles/src/scripts/media_server/js/client.js
// @supportURL      https://github.com/Zen-Path/flexycon/tree/main/dotfiles/src/scripts/media_server
// @homepageURL     https://github.com/Zen-Path/flexycon
// @icon            https://www.svgrepo.com/show/230395/download.svg
// @grant           GM_registerMenuCommand
// @grant           GM_xmlhttpRequest
// @noframes
// ==/UserScript==

const SERVER_PORT = "5000";

function downloadMedia(urls, type, range) {
    const payload = { urls, type };
    if (range !== undefined) {
        payload.range = range;
    }
    const requestData = JSON.stringify(payload);

    GM_xmlhttpRequest({
        method: "POST",
        url: `http://localhost:${SERVER_PORT}/media/download`,
        headers: { "Content-Type": "application/json" },
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

            // Remove terminal codes from the command's output
            // for example: '\n\u001b[1;33m[download][warning] OSError'
            const output_fmt = data.output
                .replace(/\u001b\[[0-9;]*m/g, "")
                .trim();

            console.log(
                ":: Download info",
                `
- request_status: ${response.status}
- process_return_code: ${data.return_code}
- output:\n${output_fmt}`
            );

            if (output_fmt.includes("[ytdl][error]")) {
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
