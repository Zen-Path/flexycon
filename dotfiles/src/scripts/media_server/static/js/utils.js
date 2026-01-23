/**
 * Copies text to clipboard with fallback and returns success status.
 * @param {any} data
 * @returns {Promise<boolean>}
 */
export async function copyToClipboard(data) {
    // Convert everything to a string
    let text;

    // Handle Object/Array serialization
    if (typeof data === "object" && data !== null) {
        try {
            text = JSON.stringify(data, null, 4);
        } catch (e) {
            console.error("Failed to stringify object for clipboard", e);
            return false;
        }
    } else {
        // Handle strings, numbers, and null/undefined
        text = String(data ?? "");
    }

    if (!text) return false;

    // Modern API
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.warn("Navigator clipboard failed:", err);
        }
    }
}

export function toLocalStandardTime(isoString) {
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

export function formatDuration(ms) {
    if (!ms || isNaN(ms)) return "0s";

    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
}

export function debounce(func, delay = 250) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

export function handleColorScheme() {
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

export class StreamManager {
    constructor(url) {
        this.url = url;
        this.source = null;
    }

    connect(onUpdate) {
        this.source = new EventSource(this.url);

        this.source.onmessage = (event) => {
            const payload = JSON.parse(event.data);
            onUpdate(payload);
        };

        window.addEventListener("beforeunload", () => this.disconnect());
    }

    disconnect() {
        if (this.source) {
            this.source.close();
            this.source = null;
            console.log("Stream disconnected.");
        }
    }
}
