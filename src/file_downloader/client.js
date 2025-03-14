// ==UserScript==
// @name        File Downloader
// @namespace   Violentmonkey Scripts
// @match       http*://*/*
// @grant       GM_registerMenuCommand
// @version     0.0.1
// @author      me
// @description Automatically download a file
// @downloadURL ***
// @supportURL
// @homepageURL
// ==/UserScript==

async function downloadGalleries(urls) {
    try {
        const response = await fetch(
            "http://localhost:5000/download_galleries",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ urls }),
            }
        );

        const data = await response.json();

        if (!response.ok) {
            console.error("Error:", data.error);
        } else {
            console.log("Download Output:", data.output);
            alert("Download complete!");
        }
    } catch (err) {
        console.error("Request failed:", err);
    }
}

function main() {
    const currentUrl = window.location.href;
    GM_registerMenuCommand("Download Gallery", () =>
        downloadGalleries([currentUrl])
    );
}

main();
