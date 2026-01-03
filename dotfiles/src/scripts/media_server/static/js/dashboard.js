/**
 * REPRESENTS A SINGLE ROW COMPONENT
 */
class EntryRow {
    constructor(data) {
        this.id = data.id;
        this.url = data.url;
        this.title = data.title || "No Title Found";
        this.mediaType = data.media_type;
        this.startTime = data.start_time;

        this.isSelected = false;
        this.isVisible = true;

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

        // 1. Checkbox
        const tdCheck = document.createElement("td");
        tdCheck.className = "col-check";
        this.dom.checkbox = document.createElement("input");
        this.dom.checkbox.type = "checkbox";
        this.dom.checkbox.onchange = (e) => this.setSelected(e.target.checked);
        tdCheck.appendChild(this.dom.checkbox);

        // 2. ID
        const tdId = document.createElement("td");
        tdId.className = "col-id";
        tdId.textContent = `#${this.id}`;

        // 3. Type
        this.dom.typeCell = document.createElement("td");
        this.dom.typeCell.className = "col-type";
        this.updateTypeIcon();

        // 4. Title/URL
        this.dom.titleCell = document.createElement("td");
        this.dom.titleCell.className = "col-title";
        this.renderTitleCell();

        // 5. Time
        const tdTime = document.createElement("td");
        tdTime.className = "col-time";
        tdTime.textContent = this.startTime;

        // 6. Actions (Dropdown Menu)
        const tdActions = document.createElement("td");
        tdActions.className = "col-actions";
        tdActions.innerHTML = `
            <div class="dropdown">
                <button class="action-btn menu-trigger"><i class="fa-solid fa-ellipsis-vertical"></i></button>
                <div class="dropdown-content">
                    <a href="#" class="menu-item js-edit"><i class="fa-solid fa-pen"></i> Edit</a>
                    <a href="#" class="menu-item js-copy-title"><i class="fa-solid fa-quote-left"></i> Copy Title</a>
                    <a href="#" class="menu-item js-copy-url"><i class="fa-solid fa-link"></i> Copy URL</a>
                    <hr>
                    <a href="#" class="menu-item danger js-delete"><i class="fa-solid fa-trash"></i> Delete</a>
                </div>
            </div>`;

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
        link.innerHTML =
            this.title !== "No Title Found"
                ? `<span class="title-text" title="${this.title}">${this.title}</span><span class="url-subtext">${this.url}</span>`
                : `<span class="title-text">${this.url}</span>`;
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
        this.dom.typeCell.innerHTML = `<div class="type-badge ${t.class}"><div class="icon-box"><i class="fa-solid ${t.icon}"></i></div><span>${t.label}</span></div>`;
    }

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

function getActiveIds() {
    const selected = Array.from(entryMap.values()).filter((e) => e.isSelected);
    if (selected.length > 0) return selected.map((e) => e.id);
    return Array.from(entryMap.values())
        .filter((e) => e.isVisible)
        .map((e) => e.id);
}

/**
 * UNIFIED ACTIONS
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
            entryMap.get(id)?.remove();
            entryMap.delete(id);
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
    if (newTitle.trim() !== "" || ids.length === 1) payload.title = newTitle;

    Promise.all(
        ids.map((id) =>
            fetch(`/api/entry/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": apiKey,
                },
                body: JSON.stringify(payload),
            })
        )
    ).then(() => {
        ids.forEach((id) => entryMap.get(id)?.update(payload));
        closeModal();
    });
}

/**
 * UI EVENT HANDLERS
 */
function filterTable() {
    const term = document.getElementById("searchInput").value.toLowerCase();
    document.getElementById("clearBtn").style.display =
        term.length > 0 ? "block" : "none";
    entryMap.forEach((e) =>
        e.setVisibility(
            e.title.toLowerCase().includes(term) ||
                e.url.toLowerCase().includes(term)
        )
    );
}

function clearSearch() {
    document.getElementById("searchInput").value = "";
    filterTable();
}

function toggleSelectAll(checked) {
    entryMap.forEach((e) => {
        if (e.isVisible) e.setSelected(checked);
    });
}

function closeModal() {
    document.getElementById("editModal").style.display = "none";
}

function sortTable(col) {
    if (currentSortCol === col) currentSortDir *= -1;
    else {
        currentSortCol = col;
        currentSortDir = 1;
    }

    const sorted = Array.from(entryMap.values()).sort(
        (a, b) => (a[col] < b[col] ? -1 : 1) * currentSortDir
    );
    const frag = document.createDocumentFragment();
    sorted.forEach((e) => frag.appendChild(e.dom.row));
    tableBody.appendChild(frag);

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

// BOOTSTRAP
document.addEventListener("DOMContentLoaded", () => {
    handleColorScheme();

    // Initial Data
    fetch("/api/history", { headers: { "X-API-Key": apiKey } })
        .then((res) => res.json())
        .then((data) => {
            data.forEach((item) => {
                const e = new EntryRow(item);
                entryMap.set(item.id, e);
                tableBody.appendChild(e.dom.row);
            });
            sortTable("id");
        });

    // Dropdown Event Delegation
    document.addEventListener("click", (e) => {
        const trigger = e.target.closest(".menu-trigger");
        document.querySelectorAll(".dropdown-content").forEach((c) => {
            if (trigger && c === trigger.nextElementSibling)
                c.classList.toggle("show");
            else c.classList.remove("show");
        });
    });

    // Global Bindings
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
