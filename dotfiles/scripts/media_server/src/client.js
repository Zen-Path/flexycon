// ==UserScript==
// @name            File Downloader
// @namespace       User Scripts
// @match           http*://*/*
// @version         1.3.0
// @author          Me
// @description     Send a download request for a URL to a local media server
// @downloadURL     ***
// @grant           GM_registerMenuCommand
// @grant           GM_xmlhttpRequest
// @supportURL
// @homepageURL
// ==/UserScript==

const SERVER_PORT = "5000";

function downloadMedia(urls, type) {
    const requestData = JSON.stringify({ urls, type });

    GM_xmlhttpRequest({
        method: "POST",
        url: `http://localhost:${SERVER_PORT}/downloadMedia`,
        headers: { "Content-Type": "application/json" },
        data: requestData,
        onload: function (response) {
            try {
                console.log("response.status=", response.status);
                const data = JSON.parse(response.responseText);

                if (response.status === 200) {
                    console.log(
                        `:: Download output:
${Array.isArray(data.output) ? data.output.join("") : data.output}`
                    );
                    alert("Download complete!");
                } else {
                    console.error(
                        `:: Response status: ${response.status}`,
                        data.error
                    );
                    alert("Download failed.");
                }
            } catch (err) {
                console.error(":: Media server", err);
                alert("Download failed.");
            }
        },
        onerror: function (error) {
            console.error(":: Media server", error);
            alert("Download failed.");
        },
    });
}

function main() {
    const currentUrl = window.location.href;
    GM_registerMenuCommand("Download Gallery", () =>
        downloadMedia([currentUrl], "gallery")
    );
    GM_registerMenuCommand("Download Galleries", () => {
        const userInput = prompt("Paste the gallery urls.");
        const galleryUrls = userInput.split(" ");
        downloadMedia(galleryUrls, "gallery");
    });
}

main();
