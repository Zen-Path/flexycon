/**
 * REPRESENTS A SINGLE ROW IN THE TABLE
 */
class EntryRow {
    constructor(data) {
        // Data Properties
        this.id = data.id;
        this.url = data.url;
        this.title = data.title;
        this.mediaType = data.media_type;
        this.startTime = data.start_time;
        this.endTime = data.endTime;

        // State
        this.isSelected = false;
        this.isVisible = true;

        // DOM References
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

        // Checkbox
        const tdCheck = document.createElement("td");
        tdCheck.className = "col-check";
        this.dom.checkbox = document.createElement("input");
        this.dom.checkbox.type = "checkbox";
        this.dom.checkbox.onchange = (e) => this.setSelected(e.target.checked);
        tdCheck.appendChild(this.dom.checkbox);

        // ID
        const tdId = document.createElement("td");
        tdId.className = "col-id";
        tdId.textContent = `#${this.id}`;

        // Type Icon
        this.dom.typeCell = document.createElement("td");
        this.dom.typeCell.className = "col-type";
        this.updateTypeIcon();

        // Title/URL
        this.dom.titleCell = document.createElement("td");
        this.dom.titleCell.className = "col-title";
        this.renderTitleCell();

        // Time
        const tdTime = document.createElement("td");
        tdTime.className = "col-time";
        tdTime.textContent = this.startTime;

        // Actions (Dropdown Menu)
        const tdActions = document.createElement("td");
        tdActions.className = "col-actions";
        tdActions.innerHTML = `
            <div class="dropdown">
                <button class="action-btn menu-trigger" title="Actions">
                    <i class="fa-solid fa-ellipsis-vertical"></i>
                </button>
                <div class="dropdown-content">
                    <a href="#" class="menu-item edit-item"><i class="fa-solid fa-pen"></i> Edit</a>
                    <a href="#" class="menu-item copy-title-item"><i class="fa-solid fa-quote-left"></i> Copy Title</a>
                    <a href="#" class="menu-item copy-url-item"><i class="fa-solid fa-link"></i> Copy URL</a>
                    <hr>
                    <a href="#" class="menu-item delete-item danger"><i class="fa-solid fa-trash"></i> Delete</a>
                </div>
            </div>
        `;

        const trigger = tdActions.querySelector(".menu-trigger");
        const content = tdActions.querySelector(".dropdown-content");

        // Toggle dropdown
        trigger.onclick = (e) => {
            e.stopPropagation();
            // Close other open dropdowns first
            document.querySelectorAll(".dropdown-content.show").forEach((d) => {
                if (d !== content) d.classList.remove("show");
            });
            content.classList.toggle("show");
        };

        // Assign Actions
        tdActions.querySelector(".edit-item").onclick = () =>
            window.openEditModal(this.id);
        tdActions.querySelector(".copy-title-item").onclick = () =>
            this.copyToClipboard(this.title, "Title");
        tdActions.querySelector(".copy-url-item").onclick = () =>
            this.copyToClipboard(this.url, "URL");
        tdActions.querySelector(".delete-item").onclick = () =>
            window.deleteEntry(this.id);

        this.dom.row.append(
            tdCheck,
            tdId,
            this.dom.typeCell,
            this.dom.titleCell,
            tdTime,
            tdActions
        );

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
        const hasTitle = this.title && this.title !== "No Title Found";
        const link = document.createElement("a");
        link.href = this.url;
        link.target = "_blank";

        if (hasTitle) {
            link.innerHTML = `<span class="title-text" title="${this.title}">${this.title}</span><span class="url-subtext">${this.url}</span>`;
        } else {
            link.innerHTML = `<span class="title-text">${this.url}</span>`;
        }
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

    copyToClipboard(text, label) {
        navigator.clipboard.writeText(text).then(() => {
            console.log(`${label} copied to clipboard`);
            // Optional: You could trigger a small toast notification here
        });
    }

    // --- Instance API ---
    update(newData) {
        if (newData.title !== undefined) {
            this.title = newData.title;
            this.renderTitleCell();
        }
        if (newData.mediaType !== undefined) {
            this.mediaType = newData.mediaType;
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
let currentSortDir = -1;
const apiKey = window.MEDIA_SERVER_KEY;

// HELPER: Determine which items to act on (Selected OR Visible)
function getActiveEntries() {
    const selected = Array.from(entryMap.values()).filter((e) => e.isSelected);
    if (selected.length > 0) return selected;
    return Array.from(entryMap.values()).filter((e) => e.isVisible);
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
    const input = document.getElementById("searchInput");
    input.value = "";
    filterTable();
    input.focus();
}

function sortTable(col) {
    if (currentSortCol === col) {
        currentSortDir *= -1;
    } else {
        currentSortCol = col;
        currentSortDir = 1;
    }

    const sorted = Array.from(entryMap.values()).sort((a, b) => {
        let valA = a[col];
        let valB = b[col];

        if (col === "title") {
            valA = (a.title || a.url).toLowerCase();
            valB = (b.title || b.url).toLowerCase();
        }

        if (valA < valB) return -1 * currentSortDir;
        if (valA > valB) return 1 * currentSortDir;
        return 0;
    });

    const fragment = document.createDocumentFragment();
    sorted.forEach((entry) => fragment.appendChild(entry.dom.row));
    tableBody.appendChild(fragment);

    // Update header icons
    document
        .querySelectorAll("th")
        .forEach((th) => th.classList.remove("active", "asc", "desc"));
    const activeTh = document.getElementById(`th-${col}`);
    if (activeTh) {
        activeTh.classList.add("active", currentSortDir === 1 ? "asc" : "desc");
    }
}

function toggleSelectAll(checked) {
    entryMap.forEach((entry) => {
        if (entry.isVisible) entry.setSelected(checked);
    });
}

function copyVisibleUrls() {
    const targets = getActiveEntries();
    if (targets.length === 0) return alert("Nothing to copy");
    const text = targets.map((e) => e.url).join("\n");
    navigator.clipboard
        .writeText(text)
        .then(() => alert(`Copied ${targets.length} URLs`));
}

function openEditModal(id) {
    const entry = entryMap.get(id);
    if (!entry) return;
    document.getElementById("editId").value = entry.id;
    document.getElementById("editTitle").value = entry.title;
    document.getElementById("editMediaType").value = entry.mediaType;
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
        headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
        body: JSON.stringify({ title: newTitle, media_type: newType }),
    }).then(() => {
        entryMap.get(id)?.update({ title: newTitle, mediaType: newType });
        closeModal();
    });
}

function deleteEntry(id) {
    if (!confirm("Delete this entry?")) return;
    fetch(`/api/entry/${id}`, {
        method: "DELETE",
        headers: { "X-API-Key": apiKey },
    }).then(() => {
        entryMap.get(id)?.remove();
        entryMap.delete(id);
    });
}

function deleteVisible() {
    const targets = getActiveEntries();
    if (targets.length === 0) return;
    if (!confirm(`Delete ${targets.length} entries?`)) return;

    const ids = targets.map((e) => e.id);
    fetch("/api/delete_bulk", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
        body: JSON.stringify({ ids }),
    }).then(() => {
        ids.forEach((id) => {
            entryMap.get(id)?.remove();
            entryMap.delete(id);
        });
        document.getElementById("selectAll").checked = false;
    });
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

// MAIN INIT
document.addEventListener("DOMContentLoaded", () => {
    handleColorScheme();

    fetch("/api/history", { headers: { "X-API-Key": apiKey } })
        .then((res) => res.json())
        .then((data) => {
            data.forEach((item) => addEntry(item));
            sortTable("id");
        });

    const eventSource = new EventSource(`/api/stream?api_key=${apiKey}`);
    eventSource.onmessage = (e) => addEntry(JSON.parse(e.data), true);

    // Global click listener to close dropdowns
    window.onclick = (event) => {
        if (
            !event.target.matches(".menu-trigger") &&
            !event.target.closest(".menu-trigger")
        ) {
            document
                .querySelectorAll(".dropdown-content")
                .forEach((dropdown) => {
                    dropdown.classList.remove("show");
                });
        }
    };

    // Re-bind the new dropdown triggers for the header
    const headerTrigger = document.querySelector(".button-group .menu-trigger");
    const headerContent = document.querySelector(
        ".button-group .dropdown-content"
    );
    if (headerTrigger) {
        headerTrigger.onclick = (e) => {
            e.stopPropagation();
            headerContent.classList.toggle("show");
        };
    }

    // BINDINGS
    window.sortTable = sortTable;
    window.filterTable = filterTable;
    window.clearSearch = clearSearch;
    window.toggleSelectAll = toggleSelectAll;
    window.copyVisibleUrls = copyVisibleUrls;
    window.deleteVisible = deleteVisible;
    window.openEditModal = openEditModal;
    window.closeModal = closeModal;
    window.saveEdit = saveEdit;
    window.deleteEntry = deleteEntry;
});
