// ==UserScript==
// @name            File Downloader
// @namespace       Flexycon
// @match           http*://*/*
// @version         1.3.12
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

function downloadMedia(urls, type) {
    const requestData = JSON.stringify({ urls, type });

    GM_xmlhttpRequest({
        method: "POST",
        url: `http://localhost:${SERVER_PORT}/downloadMedia`,
        headers: { "Content-Type": "application/json" },
        data: requestData,
        onerror: function (error) {
            console.error(":: Download failed", error);
            alert("Download failed.");
        },
        onload: function (response) {
            const data = JSON.parse(response.responseText);

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

            if (
                data.return_code !== 0 ||
                response.status !== 200 ||
                output_fmt.includes("[ytdl][error]")
            ) {
                alert("Download failed.");
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
    GM_registerMenuCommand("Download Galleries", () => {
        const userInput = prompt("Paste the gallery urls.");
        const galleryUrls = userInput.split(" ");
        downloadMedia(galleryUrls, "gallery");
    });
}

main();
