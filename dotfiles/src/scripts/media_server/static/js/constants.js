// Mirror of EventType Enum
// prettier-ignore
export const EVENT_TYPE = Object.freeze({
    CREATE:     0,
    UPDATE:     1,
    DELETE:     2,
    PROGRESS:   3,
});

// Mirror of MediaType Enum
// prettier-ignore
export const MEDIA_TYPE = Object.freeze({
    GALLERY:    0,
    IMAGE:      1,
    VIDEO:      2,
    AUDIO:      3,
    TEXT:       4,
});

export const VALID_MEDIA_TYPES = Object.values(MEDIA_TYPE);

export const MEDIA_TYPE_CONFIG = Object.freeze({
    [MEDIA_TYPE.GALLERY]: {
        icon: "fa-layer-group",
        className: "type-gallery",
        label: "Gallery",
    },
    [MEDIA_TYPE.IMAGE]: {
        icon: "fa-image",
        className: "type-image",
        label: "Image",
    },
    [MEDIA_TYPE.VIDEO]: {
        icon: "fa-film",
        className: "type-video",
        label: "Video",
    },
    [MEDIA_TYPE.AUDIO]: {
        icon: "fa-microphone",
        className: "type-audio",
        label: "Audio",
    },
    [MEDIA_TYPE.TEXT]: {
        icon: "fa-file-lines",
        className: "type-text",
        label: "Text",
    },
    UNKNOWN: {
        icon: "fa-circle-question",
        className: "type-unknown",
        label: "Unknown",
    },
});

export class ColumnData {
    constructor({
        id,
        label = null,
        field = null,
        sortable = false,
        cssClass = null,
    }) {
        this.id = id;
        this.label = label;
        this.field = field;
        this.sortable = sortable;
        this.cssClass = cssClass;
    }
}
