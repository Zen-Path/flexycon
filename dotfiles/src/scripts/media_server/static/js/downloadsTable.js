import { BaseDataRow, BaseDataTable } from "./baseDataTable.js";
import {
    VALID_MEDIA_TYPES,
    MEDIA_TYPE_CONFIG,
    ColumnData,
    STATUS_CONFIG,
    DOWNLOAD_STATUS,
} from "./constants.js";
import { toLocalStandardTime, formatDuration } from "./utils.js";
import { createMenuTrigger } from "./dropdownHelper.js";
import { ModalManager } from "./modalManager.js";
import { copyToClipboard, createIconLabelPair } from "./utils.js";

export class DownloadsTable extends BaseDataTable {
    constructor(container) {
        super(container);

        this.columnsMap = {
            CHECKBOX: new ColumnData({
                id: "checkbox",
                field: "isSelected",
                sortable: true,
                cssClass: "col-checkbox",
            }),
            ID: new ColumnData({
                id: "id",
                label: "ID",
                field: "id",
                sortable: true,
                cssClass: "col-id",
                icon: "fa-hashtag",
            }),
            MEDIA_TYPE: new ColumnData({
                id: "media-type",
                label: "Media Type",
                field: "mediaType",
                sortable: true,
                cssClass: "col-media-type",
                icon: "fa-image",
            }),
            NAME: new ColumnData({
                id: "name",
                label: "Name",
                field: "title",
                sortable: true,
                cssClass: "col-name",
                icon: "fa-quote-left",
            }),
            START_TIME: new ColumnData({
                id: "start-time",
                label: "Start Time",
                field: "startTime",
                sortable: true,
                cssClass: "col-start-time",
                icon: "fa-clock",
            }),
            STATUS: new ColumnData({
                id: "status",
                label: "Status",
                field: "status",
                sortable: true,
                cssClass: "col-status",
                icon: "fa-circle-check",
            }),
            ACTIONS: new ColumnData({
                id: "actions",
                cssClass: "col-actions",
            }),
        };
        this.columnsList = Object.values(this.columnsMap);

        this.init();
    }

    add(data) {
        this._addEntries(data, DownloadRow, this);
    }

    _createActions() {
        const actions = [
            {
                label: "Edit Selected",
                icon: "fa-pen",
                onClick: () => {
                    ModalManager.openEdit(this.getSelectedEntries());
                },
            },
            {
                label: "Copy Selected URLs",
                icon: "fa-link",
                onClick: async () => {
                    return await this.copyFields("url", true);
                },
            },
            {
                label: "Copy Selected Titles",
                icon: "fa-quote-left",
                onClick: async () => {
                    return await this.copyFields("title", true);
                },
            },
            {
                label: "Delete Selected",
                icon: "fa-trash",
                className: "text-danger",
                onClick: () => {
                    const ids = this.getSelectedEntries().map(
                        (item) => item.data.id
                    );
                    window.bulkDelete(ids);
                },
            },
        ];

        return createMenuTrigger(actions);
    }

    getStatsString() {
        const total = this.entryList.length;
        if (total === 0) return "Table is empty.";

        const selected = this.selectedCount;
        const visible = this.entryList.filter((e) => e._isVisible).length;

        // Build frequency maps dynamically
        const stats = this.entryList.reduce(
            (acc, entry) => {
                const { mediaType, status } = entry.data;
                acc.mediaTypes[mediaType] =
                    (acc.mediaTypes[mediaType] || 0) + 1;
                acc.statuses[status] = (acc.statuses[status] || 0) + 1;
                return acc;
            },
            { mediaTypes: {}, statuses: {} }
        );

        const formatGroup = (title, dataMap, config) => {
            let str = `\n[ ${title} ]\n`;
            Object.entries(dataMap).forEach(([key, count]) => {
                const label = config[key]?.label || `Unknown (${key})`;
                str += `  - ${label.padEnd(15)}: ${count}\n`;
            });
            return str;
        };

        let report = `=== Table Summary (${new Date().toLocaleTimeString()}) ===\n`;
        report += `Total Rows:      ${total}\n`;
        report += `Selected:        ${selected} (${((selected / total) * 100).toFixed(1)}%)\n`;
        report += `Visible:         ${visible} / ${total}\n`;

        // Distribution sections
        report += formatGroup(
            "Media Types",
            stats.mediaTypes,
            MEDIA_TYPE_CONFIG
        );
        report += formatGroup("Statuses", stats.statuses, STATUS_CONFIG);

        return report;
    }
}

export class DownloadRow extends BaseDataRow {
    initData(data) {
        if (!(typeof data.id === "number")) {
            data.id = -1;
        }

        if (
            !(
                typeof data.mediaType === "number" &&
                VALID_MEDIA_TYPES.includes(data.mediaType)
            )
        ) {
            data.mediaType = -1;
        }

        if (!(typeof data.title === "string" && data.title.trim().length > 0)) {
            data.title = null;
        }

        if (!(typeof data.url === "string" && data.url.trim().length > 0)) {
            data.url = null;
        }

        if (
            !(
                typeof data.startTime === "string" &&
                data.startTime.trim().length > 0 &&
                data.startTime.includes("Z")
            )
        ) {
            data.startTime = 0;
        }

        if (
            !(
                typeof data.endTime === "string" &&
                data.endTime.trim().length > 0 &&
                data.endTime.includes("Z")
            )
        ) {
            data.endTime = 0;
        }

        if (
            !(
                typeof data.updatedTime === "string" &&
                data.updatedTime.trim().length > 0 &&
                data.updatedTime.includes("Z")
            )
        ) {
            data.updatedTime = 0;
        }

        if (
            !(
                typeof data.status === "number" &&
                Object.values(DOWNLOAD_STATUS).includes(data.status)
            )
        ) {
            data.status = -1;
        }

        if (
            !(
                typeof data.statusMessage === "string" &&
                data.statusMessage.trim().length > 0
            )
        ) {
            data.statusMessage = null;
        }

        this.displayValues = {
            id: data.id >= 0 ? `#${data.id}` : "N/A",
            title: data.title !== null ? data.title.trim() : "Untitled",
            url: data.url !== null ? data.url.trim() : "Unknown",

            startTime:
                data.startTime !== 0
                    ? toLocalStandardTime(data.startTime)
                    : "-",
            endTime:
                data.endTime !== 0 ? toLocalStandardTime(data.endTime) : "-",
            updatedTime:
                data.updatedTime !== 0
                    ? toLocalStandardTime(data.updatedTime)
                    : "-",
        };

        this.sortValues = {
            id: data.id,
            title: (data.title ?? "").toLowerCase(),
            url: data.url ?? "",
            mediaType: data.mediaType,

            startTime:
                data.startTime !== 0 ? new Date(data.startTime).getTime() : 0,
            endTime: data.endTime !== 0 ? new Date(data.endTime).getTime() : 0,
            updateTime:
                data.updateTime !== 0 ? new Date(data.updateTime).getTime() : 0,
            status: data.status,
            isSelected: this.isSelected,
        };

        // TODO: temporary workaround until we implement proper filter UI
        this.searchIndex =
            `${this.displayValues.title} ${this.displayValues.url} ${this.displayValues.id}`.toLowerCase();
    }

    render() {
        this.dom.row = document.createElement("div");
        this.dom.row.classList.add("data-row");

        const columns = this.table.columnsMap;
        this.table.columnsList.forEach((col) => {
            const cell = document.createElement("div");
            cell.className = `cell ${col.cssClass || ""}`;

            switch (col.id) {
                case columns.CHECKBOX.id:
                    this.dom.checkbox = this.#renderCheckbox();
                    cell.append(this.dom.checkbox);
                    break;
                case columns.MEDIA_TYPE.id:
                    cell.append(this.#renderMediaContent());
                    this.dom.mediaTypeCell = cell;
                    break;
                case columns.NAME.id:
                    cell.append(this.#renderNameContent());
                    break;
                case columns.START_TIME.id:
                    cell.textContent = this.displayValues.startTime;
                    cell.title = this.#generateTimeDiffTooltip();
                    break;
                case columns.STATUS.id:
                    cell.append(this.#renderStatusContent());
                    this.dom.statusCell = cell;
                    break;
                case columns.ACTIONS.id:
                    cell.append(this.#renderActions());
                    break;
                default:
                    cell.textContent = this.displayValues[col.field] ?? "";
            }

            this.dom.row.appendChild(cell);
        });

        return this.dom.row;
    }

    #renderCheckbox() {
        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = this.isSelected;
        input.onclick = (e) => {
            this.isSelected = e.target.checked;
        };

        // Allow user to shift-click select multiple rows at a time
        input.onclick = (e) => {
            e.stopPropagation(); // Prevent sort trigger

            const currentIndex = this.table.entryList.indexOf(this);

            if (e.shiftKey && this.table.lastSelectedIndex !== null) {
                const start = Math.min(
                    this.table.lastSelectedIndex,
                    currentIndex
                );
                const end = Math.max(
                    this.table.lastSelectedIndex,
                    currentIndex
                );

                // Select everything in the range
                for (let i = start; i <= end; i++) {
                    this.table.entryList[i].isSelected = e.target.checked;
                }
            } else {
                this.isSelected = e.target.checked;
                this.table.lastSelectedIndex = currentIndex;
            }
        };

        return input;
    }

    #renderMediaContent() {
        const config =
            MEDIA_TYPE_CONFIG[this.data.mediaType] ?? MEDIA_TYPE_CONFIG.UNKNOWN;

        return createIconLabelPair({
            icon: config.icon,
            label: config.label,
            extraClasses: [config.className],
            title: config.label,
        });
    }

    #renderNameContent() {
        const container = document.createElement("a");
        container.href = this.data.url;
        container.target = "_blank";

        const titleEl = document.createElement("span");
        titleEl.classList.add("title", "truncate");
        titleEl.title = this.displayValues.title;
        titleEl.textContent = this.displayValues.title;

        const urlEl = document.createElement("span");
        urlEl.classList.add("url", "truncate");
        urlEl.title = this.displayValues.url;
        urlEl.textContent = this.displayValues.url;

        this.dom.titleEl = titleEl;
        this.dom.urlEl = urlEl;

        container.append(titleEl, urlEl);
        return container;
    }

    #generateTimeDiffTooltip() {
        const start = this.sortValues.startTime;
        const end = this.data.endTime ? this.sortValues.endTime : Date.now();

        const diff = end - start;
        const diffHumanReadable = formatDuration(diff);

        if (this.data.endTime === 0) {
            return `Download started more than ${diffHumanReadable} ago.`;
        }
        return `Finished at ${toLocalStandardTime(this.data.endTime)} (took ${diffHumanReadable})`;
    }

    #renderStatusContent() {
        const config = STATUS_CONFIG[this.data.status] ?? STATUS_CONFIG.UNKNOWN;

        return createIconLabelPair({
            icon: config.icon,
            label: config.label,
            extraClasses: [config.color],
            title: config.label,
        });
    }

    #renderActions() {
        const actions = [
            {
                label: "Edit Entry",
                icon: "fa-pen",
                onClick: () => {
                    ModalManager.openEdit(this);
                },
            },
            {
                label: "Copy Title",
                icon: "fa-quote-left",
                onClick: async () => {
                    return await copyToClipboard(this.data.title);
                },
            },
            {
                label: "Copy URL",
                icon: "fa-link",
                onClick: async () => {
                    return await copyToClipboard(this.data.url);
                },
            },
            {
                label: "Delete Entry",
                icon: "fa-trash",
                className: "text-danger",
                onClick: () => {
                    window.bulkDelete([this.data.id]);
                },
            },
        ];

        return createMenuTrigger(actions);
    }

    update(newData) {
        const supportedFields = ["title", "mediaType", "status"];
        const changedFields = Object.keys(newData).filter(
            (key) =>
                supportedFields.includes(key) &&
                newData[key] !== undefined &&
                newData[key] !== this.data[key]
        );

        if (changedFields.length === 0) return;

        changedFields.forEach((field) => {
            switch (field) {
                case "title":
                    this.data.title = newData.title;
                    this.initData(this.data);
                    if (this.dom.titleEl) {
                        this.dom.titleEl.textContent = this.displayValues.title;
                    }
                    break;

                case "mediaType":
                    this.data.mediaType = newData.mediaType;
                    if (this.dom.mediaTypeCell) {
                        this.dom.mediaTypeCell.replaceChildren(
                            this.#renderMediaContent()
                        );
                    }
                    break;

                case "status":
                    this.data.status = newData.status;
                    if (this.dom.statusCell) {
                        this.dom.statusCell.replaceChildren(
                            this.#renderStatusContent()
                        );
                    }
                    if (this.dom.startTimeEl) {
                        this.dom.startTimeEl.title =
                            this.#generateTimeDiffTooltip();
                    }
                    break;
            }
        });

        // Prevent stacking
        this.dom.row.classList.remove("row-pulse");

        // This is necessary to restart the animation if it was already playing
        void this.dom.row.offsetWidth;

        this.dom.row.classList.add("row-pulse");
        this.dom.row.addEventListener(
            "animationend",
            () => {
                this.dom.row.classList.remove("row-pulse");
            },
            { once: true }
        );

        this.initData(this.data);
    }
}
