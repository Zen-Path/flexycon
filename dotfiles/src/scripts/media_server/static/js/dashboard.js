// Mirror of the backend EventType Enum
// prettier-ignore
const EventType = Object.freeze({
    CREATE:     0,
    UPDATE:     1,
    DELETE:     2,
    PROGRESS:   3,
});

// Mirror of the backend MediaType Enum
// prettier-ignore
const MediaType = Object.freeze({
    GALLERY:    0,
    IMAGE:      1,
    VIDEO:      2,
    AUDIO:      3,
    TEXT:       4,
});

// Metadata configuration for UI rendering
const MEDIA_CONFIG = Object.freeze({
    [MediaType.GALLERY]: {
        icon: "fa-layer-group",
        className: "type-gallery",
        label: "Gallery",
    },
    [MediaType.IMAGE]: {
        icon: "fa-image",
        className: "type-image",
        label: "Image",
    },
    [MediaType.VIDEO]: {
        icon: "fa-film",
        className: "type-video",
        label: "Video",
    },
    [MediaType.AUDIO]: {
        icon: "fa-microphone",
        className: "type-audio",
        label: "Audio",
    },
    [MediaType.TEXT]: {
        icon: "fa-file-lines",
        className: "type-text",
        label: "Text",
    },
    // Fallback
    UNKNOWN: {
        icon: "fa-circle-question",
        className: "type-unknown",
        label: "Unknown",
    },
});

// UTILS

function toLocalStandardTime(isoString) {
    if (!isoString) return "-";

    const date = new Date(isoString);

    // 'sv-SE' (Sweden) results in "YYYY-MM-DD HH:mm:ss"
    return date.toLocaleString("sv-SE", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
}

// LOGIC

function addRowToData(item, isNew) {
    item.isNew = isNew;
    item.selected = false; // Initialize selection state
    allData.unshift(item);
}

// TABLE RENDER

/**
 * Generates the HTML for a media badge based on the type ID.
 * @returns {string} HTML string.
 */
function getMediaBadgeHtml(input) {
    // TODO: remove when we switch to ints on the backend
    // * @param {number} typeId - The integer value from the backend.
    const STRING_TO_ID = Object.fromEntries(
        Object.entries(MediaType).map(([key, val]) => [key.toLowerCase(), val])
    );
    const typeId =
        typeof input === "string" ? STRING_TO_ID[input.toLowerCase()] : input;

    const config = MEDIA_CONFIG[typeId] || MEDIA_CONFIG.UNKNOWN;

    return `
        <div class="type-badge ${config.className}">
            <div class="icon-box">
                <i class="fa-solid ${config.icon}"></i>
            </div>
            <span>${config.label}</span>
        </div>`.trim();
}

function renderTable() {
    const searchTerm = document
        .getElementById("searchInput")
        .value.toLowerCase();
    tableBody.innerHTML = "";

    // Sort logic
    allData.sort((a, b) => {
        let valA = a[currentSortCol];
        let valB = b[currentSortCol];

        if (currentSortCol === "title") {
            valA = (a.title || a.url).toLowerCase();
            valB = (b.title || b.url).toLowerCase();
        }
        if (valA < valB) return -1 * currentSortDir;
        if (valA > valB) return 1 * currentSortDir;
        return 0;
    });

    // Render Loop
    allData.forEach((row) => {
        const displayText = (row.title || row.url).toLowerCase();
        if (!displayText.includes(searchTerm)) return;

        const tr = document.createElement("tr");
        tr.classList.add("data-row");
        if (row.isNew) {
            tr.classList.add("new-row");
            row.isNew = false;
        }

        const titleDisplay = row.title ? `${row.title}` : "No Title Found";

        const localTime = toLocalStandardTime(row.startTime);

        tr.innerHTML = `
        <td class="col-check">
            <input type="checkbox" class="row-checkbox" ${row.selected ? "checked" : ""} onchange="toggleRowSelect(${row.id}, this.checked)">
        </td>
        <td class="col-id">#${row.id}</td>
        <td class="col-type">${getMediaBadgeHtml(row.mediaType)}</td>
        <td class="col-title">
            <a href="${row.url}" target="_blank">
                <span class="title-text" title="${titleDisplay}">${titleDisplay}</span>
                <span class="url-subtext">${row.url}</span>
            </a>
        </td>
        <td class="col-time">${localTime}</td>
        <td class="col-actions">
            <button class="action-btn btn-copy-title" onclick="copyItemField(${row.id}, 'title')" title="Copy Title">
                <i class="fa-solid fa-copy"></i>
            </button>
            <button class="action-btn btn-copy-url" onclick="copyItemField(${row.id}, 'url')" title="Copy URL">
                <i class="fa-solid fa-link"></i>
            </button>
            <button class="action-btn btn-edit" onclick="openEditModal(${row.id})" title="Edit">
                <i class="fa-solid fa-pen-to-square"></i>
            </button>
            <button class="action-btn btn-delete" onclick="deleteEntry(${row.id})" title="Delete">
                <i class="fa-solid fa-trash"></i>
            </button>
        </td>
    `;
        tableBody.appendChild(tr);
    });
}

// SELECTION LOGIC
function toggleRowSelect(id, isChecked) {
    const item = allData.find((r) => r.id === id);
    if (item) item.selected = isChecked;

    // Uncheck header "select all" if any row is unchecked manually
    if (!isChecked) {
        document.getElementById("selectAll").checked = false;
    }
}

function toggleSelectAll(isChecked) {
    const searchTerm = document
        .getElementById("searchInput")
        .value.toLowerCase();

    allData.forEach((row) => {
        const displayText = (row.title || row.url).toLowerCase();
        // Only affect rows that are currently visible in the search
        if (displayText.includes(searchTerm)) {
            row.selected = isChecked;
        }
    });
    renderTable();
}

/**
 * Helper to get items to act upon.
 * Priorities: 1. Checked items, 2. Visible items (if nothing checked)
 */
function getProcessableItems() {
    const selectedItems = allData.filter((row) => row.selected);
    if (selectedItems.length > 0) return selectedItems;

    const searchTerm = document
        .getElementById("searchInput")
        .value.toLowerCase();
    return allData.filter((row) => {
        const displayText = (row.title || row.url).toLowerCase();
        return displayText.includes(searchTerm);
    });
}

// SORTING
function sortTable(key) {
    if (currentSortCol === key) {
        currentSortDir *= -1; // Toggle
    } else {
        currentSortCol = key;
        currentSortDir = 1; // Default ASC
    }
    updateSortHeaders();
    renderTable();
}

function updateSortHeaders() {
    // 1. Reset all headers
    document.querySelectorAll("th").forEach((th) => {
        th.classList.remove("asc", "desc", "active");
    });

    // 2. Apply classes to active header
    const activeTh = document.getElementById(`th-${currentSortCol}`);
    if (activeTh) {
        activeTh.classList.add("active");
        activeTh.classList.add(currentSortDir === 1 ? "asc" : "desc");
    }
}

// SEARCH
function filterTable() {
    const input = document.getElementById("searchInput");
    const clearBtn = document.getElementById("clearBtn");
    // Reset select all check when filtering
    document.getElementById("selectAll").checked = false;

    // Show X if text exists
    if (input.value.length > 0) {
        clearBtn.style.display = "block";
    } else {
        clearBtn.style.display = "none";
    }
    renderTable();
}

function clearSearch() {
    const input = document.getElementById("searchInput");
    input.value = "";
    filterTable();
    input.focus();
}

// COPY
function copyVisibleUrls() {
    const itemsToCopy = getProcessableItems();

    if (itemsToCopy.length === 0) {
        alert("No URLs selected or visible to copy.");
        return;
    }

    const uniqueUrls = [...new Set(itemsToCopy.map((item) => item.url))];
    const urlsStr = uniqueUrls.join("\n");

    // Copy to clipboard
    navigator.clipboard
        .writeText(urlsStr)
        .then(() => {
            alert(`Copied ${uniqueUrls.length} URLs to clipboard!`);
        })
        .catch((err) => {
            console.error("Failed to copy: ", err);
            alert("Failed to copy to clipboard. See console for error.");
        });
}

function copyItemField(id, field) {
    const item = allData.find((r) => r.id === id);

    if (!item) {
        alert(`Item #${id} not found.`);
        return;
    }

    if (!(field in item)) {
        alert(`Field "${field}" does not exist on this item.`);
        return;
    }

    const itemField = item[field];

    navigator.clipboard
        .writeText(String(itemField))
        .then(() => {
            alert(`Copied #${id} ${field} to clipboard!`);
        })
        .catch((err) => {
            const errorMsg = `Failed to copy #${id} ${field}: ${err}`;
            console.error(errorMsg);
            alert(errorMsg);
        });
}

// EDIT

function openEditModal(id) {
    const item = allData.find((r) => r.id === id);
    if (!item) return;

    document.getElementById("editId").value = id;
    document.getElementById("editTitle").value = item.title;
    document.getElementById("editMediaType").value = item.mediaType;
    document.getElementById("editModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("editModal").style.display = "none";
}

function updateEntry(id, newTitle, newType) {
    const item = allData.find((r) => r.id === id);
    if (item) {
        item.title = newTitle;
        item.mediaType = newType;
    }
}

function saveEdit() {
    const id = parseInt(document.getElementById("editId").value);
    const newTitle = document.getElementById("editTitle").value;
    const newTypeValue = document.getElementById("editMediaType").value;

    const newType = newTypeValue === -1 ? null : parseInt(newTypeValue);

    const payload = { id, title: newTitle };
    if (newType !== "") {
        payload.mediaType = newType;
    }

    fetch(`/api/bulkEdit`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": apiKey,
        },
        body: JSON.stringify([payload]),
    })
        .then((res) => res.json())
        .then(() => {
            updateEntry(id, newTitle, newType);
            closeModal();
            renderTable();
        });
}

// DELETE

function handleDelete(payload) {
    allData = allData.filter((item) => item.id !== payload.id);
}

function deleteEntry(id) {
    if (!confirm("Are you sure you want to delete this entry?")) return;

    fetch(`/api/bulkDelete`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": apiKey,
        },
        body: JSON.stringify({ ids: [id] }),
    }).then(() => {
        allData = allData.filter((item) => item.id !== id);
        renderTable();
    });
}

function deleteVisible() {
    const itemsToDelete = getProcessableItems();

    if (itemsToDelete.length === 0) {
        alert("No items selected or visible to delete.");
        return;
    }

    if (
        !confirm(
            `Delete all ${itemsToDelete.length} selected/visible entries?  This cannot be undone.`
        )
    )
        return;

    const ids = itemsToDelete.map((item) => item.id);

    fetch("/api/bulkDelete", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": apiKey,
        },
        body: JSON.stringify({ ids: ids }),
    })
        .then((res) => res.json())
        .then((envelope) => {
            if (!envelope.status) {
                console.error("Bulk delete failed entirely:", envelope);
                alert(
                    "Could not delete items: " +
                        (envelope.error || "Unknown error")
                );
                return;
            }

            const successfullyDeletedIds = envelope.data
                .filter((item) => item.status === true)
                .map((item) => item.data); // 'data' holds the ID

            allData = allData.filter(
                (item) => !successfullyDeletedIds.includes(item.id)
            );

            const failedCount = envelope.data.filter(
                (item) => item.status === false
            ).length;

            if (failedCount > 0) {
                alert(`Could not delete ${failedCount} items.`);
                console.error("Deletion Response:", envelope);
            }

            document.getElementById("selectAll").checked = false;
            renderTable();
        })
        .catch((err) => {
            alert(`Could not delete items: ${err}.`);
            console.error("Network or server error:", err);
        });
}

function handleProgress(payload) {
    const percentage = Math.round((payload.current / payload.total) * 100);
    payload.percentage = percentage;
    console.log("Progress update: ", payload);
}

function handleColorScheme() {
    const themeToggleBtn = document.getElementById("themeToggle");
    const themeIcon = themeToggleBtn.querySelector("i");

    // Check LocalStorage or System Preference on Load
    const currentTheme = localStorage.getItem("theme");
    const systemPrefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)"
    ).matches;

    if (currentTheme === "dark" || (!currentTheme && systemPrefersDark)) {
        document.body.classList.add("dark-mode");
        themeIcon.classList.replace("fa-moon", "fa-sun"); // Change icon if needed
    }

    themeToggleBtn.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");

        let theme = "light";

        // If dark mode is now active
        if (document.body.classList.contains("dark-mode")) {
            theme = "dark";
            themeIcon.classList.replace("fa-moon", "fa-sun");
        } else {
            themeIcon.classList.replace("fa-sun", "fa-moon");
        }

        themeToggleBtn.title = `Toggle ${theme === "dark" ? "Light" : "Dark"} Mode`;

        // Save preference to localStorage
        localStorage.setItem("theme", theme);
    });
}

// MAIN

const tableBody = document.getElementById("table-body");
let allData = [];
let currentSortCol = "id";
let currentSortDir = -1; // -1 = DESC

const apiKey = window.MEDIA_SERVER_KEY;

document.addEventListener("DOMContentLoaded", () => {
    handleColorScheme();

    // Initial Load
    fetch("/api/downloads", {
        headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
    })
        .then((response) => response.json())
        .then((data) => {
            data.forEach((item) => addRowToData(item, false));
            updateSortHeaders();
            renderTable();
        });

    // Real-Time Listener
    const eventSource = new EventSource(`/api/stream?apiKey=${apiKey}`);

    eventSource.onmessage = function (event) {
        const { type, data } = JSON.parse(event.data);

        switch (type) {
            case EventType.CREATE:
                addRowToData(data, true);
                break;

            case EventType.UPDATE:
                updateEntry(data.id, data.title, data.mediaType);
                break;

            case EventType.PROGRESS:
                handleProgress(data);
                break;

            case EventType.DELETE:
                handleDelete(data);
                break;

            default:
                console.warn(`Unhandled EventType received: ${type}`);
        }

        // Refresh UI for non-progress events
        if (type !== EventType.PROGRESS) {
            renderTable();
        }
    };

    window.copyVisibleUrls = copyVisibleUrls;
    window.deleteVisible = deleteVisible;
    window.closeModal = closeModal;
    window.saveEdit = saveEdit;
    window.filterTable = filterTable;
    window.clearSearch = clearSearch;
    window.sortTable = sortTable;
    window.toggleRowSelect = toggleRowSelect;
    window.toggleSelectAll = toggleSelectAll;
    window.copyItemField = copyItemField;
});
