/**
 * REPRESENTS A SINGLE ROW COMPONENT (Retained-mode UI)
 */
class EntryRow {
    constructor(data) {
        // Explicit Data Properties
        this.id = data.id;
        this.url = data.url;
        this.title = data.title || "No Title Found";
        this.mediaType = data.media_type;
        this.startTime = data.start_time;

        // State Properties
        this.isSelected = false;
        this.isVisible = true;

        // Explicit DOM References
        this.dom = {
            row: document.createElement("tr"),
            checkbox: null,
            typeCell: null,
            titleCell: null,
        };

        this.createElement();
    }

    createElement() {
        this.dom.row.className = "data-row";
        this.dom.row.dataset.id = this.id;

        // 1. Checkbox Column
        const tdCheck = document.createElement("td");
        tdCheck.className = "col-check";
        this.dom.checkbox = document.createElement("input");
        this.dom.checkbox.type = "checkbox";
        this.dom.checkbox.onchange = (e) => this.setSelected(e.target.checked);
        tdCheck.appendChild(this.dom.checkbox);

        // 2. ID Column
        const tdId = document.createElement("td");
        tdId.className = "col-id";
        tdId.textContent = `#${this.id}`;

        // 3. Type Column (Icon)
        this.dom.typeCell = document.createElement("td");
        this.dom.typeCell.className = "col-type";
        this.updateTypeIcon();

        // 4. Title/URL Column (Fluid)
        this.dom.titleCell = document.createElement("td");
        this.dom.titleCell.className = "col-title";
        this.renderTitleCell();

        // 5. Time Column
        const tdTime = document.createElement("td");
        tdTime.className = "col-time";
        tdTime.textContent = this.startTime;

        // 6. Actions (Dropdown Menu)
        const tdActions = document.createElement("td");
        tdActions.className = "col-actions";
        tdActions.innerHTML = `
            <div class="dropdown">
                <button class="action-btn menu-trigger" title="Actions">
                    <i class="fa-solid fa-ellipsis-vertical"></i>
                </button>
                <div class="dropdown-content">
                    <a href="#" class="menu-item js-edit"><i class="fa-solid fa-pen"></i> Edit</a>
                    <a href="#" class="menu-item js-copy-title"><i class="fa-solid fa-quote-left"></i> Copy Title</a>
                    <a href="#" class="menu-item js-copy-url"><i class="fa-solid fa-link"></i> Copy URL</a>
                    <hr>
                    <a href="#" class="menu-item danger js-delete"><i class="fa-solid fa-trash"></i> Delete</a>
                </div>
            </div>`;

        // Bind Unified Actions (Pass ID as an array [id])
        tdActions.querySelector(".js-edit").onclick = () =>
            window.unifiedEdit([this.id]);
        tdActions.querySelector(".js-copy-title").onclick = () =>
            window.unifiedCopy([this.id], "title");
        tdActions.querySelector(".js-copy-url").onclick = () =>
            window.unifiedCopy([this.id], "url");
        tdActions.querySelector(".js-delete").onclick = () =>
            window.unifiedDelete([this.id]);

        this.dom.row.append(
            tdCheck,
            tdId,
            this.dom.typeCell,
            this.dom.titleCell,
            tdTime,
            tdActions
        );
    }

    renderTitleCell() {
        const link = document.createElement("a");
        link.href = this.url;
        link.target = "_blank";

        // Use structure that CSS can truncate with ellipsis
        link.innerHTML =
            this.title !== "No Title Found"
                ? `<span class="title-text" title="${this.title}">${this.title}</span><span class="url-subtext" title="${this.url}">${this.url}</span>`
                : `<span class="title-text" title="${this.url}">${this.url}</span>`;

        this.dom.titleCell.innerHTML = "";
        this.dom.titleCell.appendChild(link);
    }

    updateTypeIcon() {
        const map = {
            image: { icon: "fa-image", class: "type-image", label: "Image" },
            video: { icon: "fa-film", class: "type-video", label: "Video" },
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
        const t = map[this.mediaType] || map["unknown"];
        this.dom.typeCell.innerHTML = `
            <div class="type-badge ${t.class}">
                <div class="icon-box"><i class="fa-solid ${t.icon}"></i></div>
                <span>${t.label}</span>
            </div>`;
    }

    // --- Instance API ---
    update(newData) {
        if (newData.title !== undefined) {
            this.title = newData.title;
            this.renderTitleCell();
        }
        if (newData.media_type !== undefined) {
            this.mediaType = newData.media_type;
            this.updateTypeIcon();
        }
    }

    setSelected(state) {
        this.isSelected = state;
        this.dom.checkbox.checked = state;
        this.dom.row.classList.toggle("selected-row", state);
    }

    setVisibility(visible) {
        this.isVisible = visible;
        this.dom.row.style.display = visible ? "" : "none";
    }

    markAsNew() {
        this.dom.row.classList.add("new-row");
        setTimeout(() => this.dom.row.classList.remove("new-row"), 3000);
    }

    remove() {
        this.dom.row.remove();
    }
}

/**
 * GLOBAL CONTROLLER
 */
const entryMap = new Map();
const tableBody = document.getElementById("table-body");
let currentSortCol = "id";
let currentSortDir = 1;
const apiKey = window.MEDIA_SERVER_KEY;

// HELPER: Determine which items to act on (Selected OR Visible)
function getActiveIds() {
    const selected = Array.from(entryMap.values()).filter((e) => e.isSelected);
    if (selected.length > 0) return selected.map((e) => e.id);
    return Array.from(entryMap.values())
        .filter((e) => e.isVisible)
        .map((e) => e.id);
}

function addEntry(data, isNew = false) {
    if (entryMap.has(data.id)) return;
    const entry = new EntryRow(data);
    entryMap.set(data.id, entry);

    if (isNew) {
        tableBody.prepend(entry.dom.row);
        entry.markAsNew();
    } else {
        tableBody.appendChild(entry.dom.row);
    }
}

/**
 * UNIFIED ACTION LOGIC (Works on Array of IDs)
 */

function unifiedCopy(ids, property) {
    const text = ids
        .map((id) => entryMap.get(id)?.[property])
        .filter(Boolean)
        .join("\n");
    navigator.clipboard.writeText(text);
}

function unifiedDelete(ids) {
    if (ids.length === 0) return;

    // Reality Check: Single ID/Title vs Count
    const message =
        ids.length === 1
            ? `Delete entry #${ids[0]}: "${entryMap.get(ids[0]).title}"?`
            : `Delete ${ids.length} selected entries? This cannot be undone.`;

    if (!confirm(message)) return;

    const endpoint =
        ids.length === 1 ? `/api/entry/${ids[0]}` : "/api/delete_bulk";
    fetch(endpoint, {
        method: ids.length === 1 ? "DELETE" : "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
        body: ids.length === 1 ? null : JSON.stringify({ ids }),
    }).then(() => {
        ids.forEach((id) => {
            const entry = entryMap.get(id);
            if (entry) {
                entry.remove();
                entryMap.delete(id);
            }
        });
        document.getElementById("selectAll").checked = false;
    });
}

function unifiedEdit(ids) {
    if (ids.length === 0) return;
    const modal = document.getElementById("editModal");
    const countDisplay = document.getElementById("affectedCount");

    modal.dataset.targetIds = JSON.stringify(ids);

    if (ids.length === 1) {
        const entry = entryMap.get(ids[0]);
        document.getElementById("editTitle").value = entry.title;
        document.getElementById("editMediaType").value = entry.mediaType;
        countDisplay.textContent = `Editing #${entry.id}`;
    } else {
        document.getElementById("editTitle").value = "";
        document.getElementById("editTitle").placeholder =
            "(Keep existing titles)";
        countDisplay.textContent = `Updating ${ids.length} entries`;
    }
    modal.style.display = "flex";
}

function saveEdit() {
    const modal = document.getElementById("editModal");
    const ids = JSON.parse(modal.dataset.targetIds || "[]");
    const newTitle = document.getElementById("editTitle").value;
    const newType = document.getElementById("editMediaType").value;

    const payload = { media_type: newType };
    // If bulk and title is empty, don't overwrite existing titles
    if (newTitle.trim() !== "" || ids.length === 1) {
        payload.title = newTitle;
    }

    Promise.all(
        ids.map((id) => {
            return fetch(`/api/entry/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": apiKey,
                },
                body: JSON.stringify(payload),
            });
        })
    ).then(() => {
        ids.forEach((id) => entryMap.get(id)?.update(payload));
        closeModal();
    });
}

/**
 * UI EVENT HELPERS
 */
function filterTable() {
    const term = document.getElementById("searchInput").value.toLowerCase();
    const clearBtn = document.getElementById("clearBtn");
    clearBtn.style.display = term.length > 0 ? "block" : "none";

    entryMap.forEach((entry) => {
        const match =
            entry.title.toLowerCase().includes(term) ||
            entry.url.toLowerCase().includes(term);
        entry.setVisibility(match);
    });
}

function clearSearch() {
    document.getElementById("searchInput").value = "";
    filterTable();
}

function toggleSelectAll(checked) {
    entryMap.forEach((entry) => {
        if (entry.isVisible) entry.setSelected(checked);
    });
}

function closeModal() {
    document.getElementById("editModal").style.display = "none";
}

function sortTable(col) {
    if (currentSortCol === col) {
        currentSortDir *= -1;
    } else {
        currentSortCol = col;
        currentSortDir = 1;
    }

    // 1. Get the current limit from the dropdown
    const limit = parseInt(document.getElementById("rowLimit").value);
    const searchTerm = document
        .getElementById("searchInput")
        .value.toLowerCase();

    // 2. Sort the data
    const sorted = Array.from(entryMap.values()).sort((a, b) => {
        let valA = a[col];
        let valB = b[col];
        if (col === "title") {
            valA = (a.title || a.url).toLowerCase();
            valB = (b.title || b.url).toLowerCase();
        }
        return (valA < valB ? -1 : 1) * currentSortDir;
    });

    // 3. Re-attach and Apply Limit
    const fragment = document.createDocumentFragment();
    let shownCount = 0;

    sorted.forEach((entry) => {
        const matchesSearch =
            entry.title.toLowerCase().includes(searchTerm) ||
            entry.url.toLowerCase().includes(searchTerm);

        // Logic: If it matches search AND we haven't hit the limit (or limit is 0/unlimited)
        if (matchesSearch && (limit === 0 || shownCount < limit)) {
            entry.setVisibility(true);
            shownCount++;
        } else {
            entry.setVisibility(false);
        }

        fragment.appendChild(entry.dom.row);
    });

    tableBody.appendChild(fragment);

    // Update header icons
    document
        .querySelectorAll("th")
        .forEach((th) => th.classList.remove("active", "asc", "desc"));
    document
        .getElementById(`th-${col}`)
        ?.classList.add("active", currentSortDir === 1 ? "asc" : "desc");
}

function handleColorScheme() {
    const btn = document.getElementById("themeToggle");
    const icon = btn.querySelector("i");
    const current =
        localStorage.getItem("theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light");

    if (current === "dark") document.body.classList.add("dark-mode");

    btn.onclick = () => {
        const isDark = document.body.classList.toggle("dark-mode");
        localStorage.setItem("theme", isDark ? "dark" : "light");
        icon.className = isDark ? "fas fa-sun" : "fas fa-moon";
    };
}

// MAIN INITIALIZATION
document.addEventListener("DOMContentLoaded", () => {
    handleColorScheme();

    // 1. Initial Load
    fetch("/api/history", { headers: { "X-API-Key": apiKey } })
        .then((res) => res.json())
        .then((data) => {
            data.forEach((item) => addEntry(item));
            sortTable("id");
        });

    // 2. Real-Time Listener (SSE)
    const eventSource = new EventSource(`/api/stream?api_key=${apiKey}`);
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        addEntry(data, true);
    };
    eventSource.onerror = (err) => {
        console.error("EventSource failed:", err);
        eventSource.close();
    };

    // 3. Dropdown Delegation
    document.addEventListener("click", (e) => {
        const trigger = e.target.closest(".menu-trigger");
        document.querySelectorAll(".dropdown-content").forEach((c) => {
            if (trigger && c === trigger.nextElementSibling)
                c.classList.toggle("show");
            else c.classList.remove("show");
        });
    });

    // 4. Global Bindings for HTML
    window.unifiedEdit = unifiedEdit;
    window.unifiedCopy = unifiedCopy;
    window.unifiedDelete = unifiedDelete;
    window.saveEdit = saveEdit;
    window.closeModal = closeModal;
    window.filterTable = filterTable;
    window.clearSearch = clearSearch;
    window.toggleSelectAll = toggleSelectAll;
    window.sortTable = sortTable;
    window.getActiveIds = getActiveIds;
});
