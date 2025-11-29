//
const OVERLAY_ID = "gm-url-extractor-overlay";

// Prevent multiple overlays
if (document.getElementById(OVERLAY_ID)) {
    return Promise.resolve(null);
}

let resolveForm;
const formPromise = new Promise((resolve) => {
    resolveForm = resolve;
});

// We capture the return object (HTMLStyleElement) to remove it later
const styleElement = GM_addStyle(STYLES);

const overlay = GM_addElement(document.body, "div", {
    id: OVERLAY_ID,
});

function closeOverlay() {
    if (overlay) overlay.remove();
    if (styleElement) styleElement.remove();
}

// HTML

overlay.innerHTML = `
<div class="gm-overlay-box">
    <h2 class="gm-overlay-title">URL Extractor</h2>

    <!-- URL Input -->
    <div>
        <label class="gm-label">Paste URLs (One per line)</label>
        <textarea id="gm-url-input" class="gm-textarea" placeholder="https://...">${window.location.href}</textarea>
        <div id="gm-url-log" class="gm-log">Found 0 urls</div>
    </div>

    <!-- Media Type Dropdown -->
    <div>
        <label class="gm-label">Media Type</label>
        <select id="gm-media-select" class="gm-select">
            ${Object.values(MEDIA_TYPES)
                .map((val) => {
                    const isSelected =
                        val === MEDIA_TYPES.UNKNOWN ? "selected" : "";
                    return `<option value="${val}" ${isSelected}>${val}</option>`;
                })
                .join("")}
        </select>
    </div>

    <!-- Range Inputs -->
    <div>
        <label class="gm-label">Range (Start : End)</label>
        <div class="gm-row">
            <input type="number" id="gm-range-start" class="gm-input" placeholder="Start">
            <span style="font-weight:bold">:</span>
            <input type="number" id="gm-range-end" class="gm-input" placeholder="End">
        </div>
    </div>

    <!-- Actions -->
    <div class="gm-actions">
        <button id="gm-btn-cancel" class="gm-btn gm-btn-cancel">Cancel</button>
        <button id="gm-btn-submit" class="gm-btn gm-btn-submit">Submit</button>
    </div>
</div>
`;

const urlInput = document.getElementById("gm-url-input");
const urlLog = document.getElementById("gm-url-log");
const rangeStart = document.getElementById("gm-range-start");
const rangeEnd = document.getElementById("gm-range-end");
const btnCancel = document.getElementById("gm-btn-cancel");
const btnSubmit = document.getElementById("gm-btn-submit");
const mediaSelect = document.getElementById("gm-media-select");

// Live URL Counter
urlInput.addEventListener("input", () => {
    const text = urlInput.value;
    const lines = text.split("\n").filter((line) => line.trim() !== "");
    urlLog.textContent = `Found ${lines.length} urls`;
});

rangeEnd.addEventListener("input", () => {
    rangeEnd.classList.remove("gm-error");
});

btnCancel.addEventListener("click", () => {
    closeOverlay();
    resolveForm(null);
});

btnSubmit.addEventListener("click", () => {
    // Validate range
    const startVal = parseInt(rangeStart.value) || null;
    const endVal = parseInt(rangeEnd.value) || null;

    if (!isNaN(startVal) && !isNaN(endVal)) {
        if (startVal > endVal) {
            rangeEnd.classList.add("gm-error");
            return; // Stop submission
        }
    }

    const rawUrls = urlInput.value
        .split("\n")
        .map((l) => l.trim())
        .filter((l) => l !== "");
    const type = mediaSelect.value;

    const result = {
        urls: rawUrls,
        mediaType: type,
        range: `${startVal === null ? "" : startVal}:${endVal === null ? "" : endVal}`,
        rangeObj: {
            start: startVal,
            end: endVal,
        },
    };

    closeOverlay();

    resolveForm(result);
});

return formPromise;
