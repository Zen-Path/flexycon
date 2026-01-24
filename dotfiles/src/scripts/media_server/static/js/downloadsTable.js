import { BaseDataRow, BaseDataTable } from "./baseDataTable.js";
import {
    VALID_MEDIA_TYPES,
    MEDIA_TYPE_CONFIG,
    ColumnData,
} from "./constants.js";
import { toLocalStandardTime, formatDuration } from "./utils.js";
import { createMenuTrigger } from "./dropdownHelper.js";
import { ModalManager } from "./modalManager.js";
import { copyToClipboard } from "./utils.js";

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
            }),
            MEDIA_TYPE: new ColumnData({
                id: "media-type",
                label: "Media Type",
                field: "mediaType",
                sortable: true,
                cssClass: "col-media-type",
            }),
            NAME: new ColumnData({
                id: "name",
                label: "Name",
                field: "title",
                sortable: true,
                cssClass: "col-name",
            }),
            START_TIME: new ColumnData({
                id: "start-time",
                label: "Start Time",
                field: "startTime",
                sortable: true,
                cssClass: "col-start-time",
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
}

export class DownloadRow extends BaseDataRow {
    constructor(container, table) {
        super(container, table);
        this.mediaTypeConfig = null;
    }

    initData(data) {
        this.mediaTypeConfig =
            MEDIA_TYPE_CONFIG[this.data.mediaType] ?? MEDIA_TYPE_CONFIG.UNKNOWN;

        this.displayValues = {
            id: typeof data.id === "number" ? `#${data.id}` : "N/A",
            title: data.title || "Untitled",
            url: data.url || "Unknown",
            mediaType: this.mediaTypeConfig.label,

            startTime: data.startTime
                ? toLocalStandardTime(data.startTime)
                : "-",
            endTime: data.endTime ? toLocalStandardTime(data.endTime) : "-",
            updatedTime: data.updatedTime
                ? toLocalStandardTime(data.updatedTime)
                : "-",

            status: data.status || "Unknown",
            statusMessage: data.statusMessage || "",
        };

        this.sortValues = {
            id: Number(data.id) || 0,
            title: (data.title || "").toLowerCase(),
            url: data.url,
            mediaType: VALID_MEDIA_TYPES.includes(data.mediaType)
                ? data.mediaType
                : -1,

            startTime: data.startTime ? new Date(data.startTime).getTime() : 0,
            endTime: data.endTime ? new Date(data.endTime).getTime() : 0,
            updateTime: data.updateTime
                ? new Date(data.updateTime).getTime()
                : 0,
            status: data.status || -1,
            isSelected: this.isSelected,
        };

        // TODO: temporary workaround until we implement proper filter UI
        this.searchIndex =
            `${this.displayValues.title} ${this.displayValues.url} ${this.displayValues.id}`.toLowerCase();
    }

    render() {
        this.initData(this.data);

        this.dom.row = document.createElement("div");
        this.dom.row.classList.add("data-row");

        const columns = this.table.columnsMap;
        this.table.columnsList.forEach((col) => {
            const cell = document.createElement("div");
            cell.className = `cell ${col.cssClass || ""}`;

            switch (col.id) {
                case columns.CHECKBOX.id:
                    const checkbox = this.#createCheckbox();

                    // Allow user to shift-click select multiple rows at a time
                    checkbox.onclick = (e) => {
                        e.stopPropagation(); // Prevent sort trigger

                        const currentIndex = this.table.entryList.indexOf(this);

                        if (
                            e.shiftKey &&
                            this.table.lastSelectedIndex !== null
                        ) {
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
                                this.table.entryList[i].isSelected =
                                    e.target.checked;
                            }
                        } else {
                            this.isSelected = e.target.checked;
                            this.table.lastSelectedIndex = currentIndex;
                        }
                    };

                    this.dom.checkbox = checkbox;
                    cell.append(this.dom.checkbox);
                    break;
                case columns.MEDIA_TYPE.id:
                    const iconEl = document.createElement("i");
                    iconEl.classList.add("fa-solid", this.mediaTypeConfig.icon);

                    const labelEl = document.createElement("span");
                    labelEl.classList.add("truncate");
                    labelEl.textContent = this.mediaTypeConfig.label;

                    cell.classList.add(this.mediaTypeConfig.className);
                    cell.append(iconEl, labelEl);
                    this.dom.mediaTypeCell = cell;
                    break;
                case columns.NAME.id:
                    cell.append(this.#createNameElems());
                    break;
                case columns.START_TIME.id:
                    cell.textContent = this.displayValues.startTime;
                    cell.title = this.#generateTimeDiffTooltip();
                    break;
                case columns.ACTIONS.id:
                    cell.append(this.#createActions());
                    break;
                default:
                    cell.textContent = this.displayValues[col.field] || "";
            }

            this.dom.row.appendChild(cell);
        });

        return this.dom.row;
    }

    #createCheckbox() {
        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = this.isSelected;
        input.onclick = (e) => {
            this.isSelected = e.target.checked;
        };
        return input;
    }

    #createNameElems() {
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

        if (this.data.endTime === undefined) {
            return `Download started more than ${diffHumanReadable} ago.`;
        }
        return `Finished at ${toLocalStandardTime(this.data.endTime)} (took ${diffHumanReadable})`;
    }

    #createActions() {
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
        const changedFields = Object.keys(newData).filter(
            (key) =>
                newData[key] !== undefined && newData[key] !== this.data[key]
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
                    const config =
                        MEDIA_TYPE_CONFIG[newData.mediaType] ??
                        MEDIA_TYPE_CONFIG.UNKNOWN;
                    if (this.dom.mediaTypeCell) {
                        this.dom.mediaTypeCell.classList.remove(
                            this.mediaTypeConfig.className
                        );
                        this.dom.mediaTypeCell.classList.add(config.className);
                        this.dom.mediaTypeCell.innerHTML = `
                        <i class="fa-solid ${config.icon}"></i>
                        <span>${config.label}</span>
                        `;
                    }
                    this.data.mediaType = newData.mediaType;
                    break;

                case "status":
                    this.data.status = newData.status;
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
