// ==UserScript==
// @name            File Downloader
// @namespace       Violentmonkey Scripts
// @match           http*://*/*
// @version         0.1.0
// @author          Me
// @description     Automatically download a file
// @downloadURL     ***
// @grant           GM_registerMenuCommand
// @grant           GM_xmlhttpRequest
// @supportURL
// @homepageURL
// ==/UserScript==

function downloadGalleries(urls) {
    const requestData = JSON.stringify({ urls });

    GM_xmlhttpRequest({
        method: "POST",
        url: "http://localhost:5000/download_galleries",
        headers: { "Content-Type": "application/json" },
        data: requestData,
        onload: function (response) {
            try {
                const data = JSON.parse(response.responseText);

                if (response.status === 200) {
                    console.log("Download Output:", data.output);
                    alert("Download complete!");
                } else {
                    console.error("Error:", data.error);
                }
            } catch (err) {
                console.error("Error parsing response:", err);
            }
        },
        onerror: function (error) {
            console.error("Request failed:", error);
        },
    });
}

function main() {
    const currentUrl = window.location.href;
    GM_registerMenuCommand("Download Gallery", () =>
        downloadGalleries([currentUrl])
    );
}

main();
