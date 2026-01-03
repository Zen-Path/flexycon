function addRowToData(item, isNew) {
    item.isNew = isNew;
    item.selected = false; // Initialize selection state
    allData.unshift(item);
}

// TABLE RENDER
function getIconHtml(type) {
    const map = {
        image: {
            icon: "fa-image",
            class: "type-image",
            label: "Image",
        },
        video: {
            icon: "fa-film",
            class: "type-video",
            label: "Video",
        },
        gallery: {
            icon: "fa-layer-group",
            class: "type-gallery",
            label: "Gallery",
        },
        unknown: {
            icon: "fa-circle-question",
            class: "type-unknown",
            label: "Unknown",
        },
    };
    const t = map[type] || map["unknown"];
    return `<div class="type-badge ${t.class}">
            <div class="icon-box"><i class="fa-solid ${t.icon}"></i></div>
            <span>${t.label}</span>
        </div>`;
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

        const titleDisplay =
            row.title && row.title !== "No Title Found"
                ? `<span class="title-text" title="${row.title}">${row.title}</span><span class="url-subtext">${row.url}</span>`
                : `<span class="title-text">${row.url}</span>`;

        tr.innerHTML = `
        <td class="col-check">
            <input type="checkbox" class="row-checkbox" ${row.selected ? "checked" : ""} onchange="toggleRowSelect(${row.id}, this.checked)">
        </td>
        <td class="col-id">#${row.id}</td>
        <td class="col-type">${getIconHtml(row.media_type)}</td>
        <td class="col-title"><a href="${row.url}" target="_blank">${titleDisplay}</a></td>
        <td class="col-time">${row.start_time}</td>
        <td class="col-actions">
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

    const urlList = itemsToCopy.map((item) => item.url).join("\n");

    // Copy to clipboard
    navigator.clipboard
        .writeText(urlList)
        .then(() => {
            alert(`Copied ${itemsToCopy.length} URLs to clipboard!`);
        })
        .catch((err) => {
            console.error("Failed to copy: ", err);
            alert("Failed to copy to clipboard. See console for error.");
        });
}

// EDIT

function openEditModal(id) {
    const item = allData.find((r) => r.id === id);
    if (!item) return;

    document.getElementById("editId").value = id;
    document.getElementById("editTitle").value = item.title;
    document.getElementById("editMediaType").value = item.media_type;
    document.getElementById("editModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("editModal").style.display = "none";
}

function saveEdit() {
    const id = parseInt(document.getElementById("editId").value);
    const newTitle = document.getElementById("editTitle").value;
    const newType = document.getElementById("editMediaType").value;

    fetch(`/api/entry/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": apiKey,
        },
        body: JSON.stringify({
            title: newTitle,
            media_type: newType,
        }),
    })
        .then((res) => res.json())
        .then(() => {
            // Update local memory
            const item = allData.find((r) => r.id === id);
            if (item) {
                item.title = newTitle;
                item.media_type = newType;
            }
            closeModal();
            renderTable();
        });
}

// DELETE

function deleteEntry(id) {
    if (!confirm("Are you sure you want to delete this entry?")) return;

    fetch(`/api/entry/${id}`, {
        method: "DELETE",
        headers: {
            "X-API-Key": apiKey,
        },
    }).then(() => {
        // Remove from local array
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

    fetch("/api/delete_bulk", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": apiKey,
        },
        body: JSON.stringify({ ids: ids }),
    })
        .then((res) => res.json())
        .then(() => {
            // Remove deleted IDs from local memory
            allData = allData.filter((item) => !ids.includes(item.id));
            document.getElementById("selectAll").checked = false;
            renderTable();
        });
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
    fetch("/api/history", {
        headers: { "X-API-Key": apiKey },
    })
        .then((response) => response.json())
        .then((data) => {
            data.forEach((item) => addRowToData(item, false));
            updateSortHeaders();
            renderTable();
        });

    // Real-Time Listener
    const eventSource = new EventSource(`/api/stream?api_key=${apiKey}`);
    eventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);
        addRowToData(data, true);
        renderTable();
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
});
