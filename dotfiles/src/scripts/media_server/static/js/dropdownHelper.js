// State management for the module
let activeDropdownMenu = null;

/**
 * Creates the ellipsis trigger button.
 */
export function createMenuTrigger(actions) {
    const container = document.createElement("div");
    container.className = "dropdown";

    const btn = document.createElement("button");
    btn.className = "action-btn";
    btn.innerHTML = `<i class="fa-solid fa-ellipsis-vertical"></i>`;

    btn.onclick = (e) => {
        e.stopPropagation();

        // Check if this specific menu is already open
        const isSelf =
            activeDropdownMenu &&
            activeDropdownMenu.parentElement === container;

        closeActiveMenu();

        // If we didn't just close ourselves, create and show a new menu
        if (!isSelf) {
            const menu = renderDropdownMenu(actions);
            container.appendChild(menu);
            activeDropdownMenu = menu;
        }
    };

    container.appendChild(btn);
    return container;
}

/**
 * Generates the actual dropdown HTML on demand.
 */
function renderDropdownMenu(actions) {
    const menu = document.createElement("div");
    menu.className = "dropdown-content";

    actions.forEach((action) => {
        const btn = document.createElement("button");
        btn.className = `menu-item`;

        const iconEl = document.createElement("i");
        iconEl.className = `fa-solid ${action.icon} ${action.className || ""}`;

        const labelEl = document.createElement("span");
        labelEl.textContent = action.label;

        btn.append(iconEl, labelEl);

        btn.onclick = async (e) => {
            e.stopPropagation();

            const result = await action.onClick();

            // Handle the Success/Failure Icon Swap
            if (typeof result === "boolean") {
                const originalClass = action.icon;
                const feedbackClass = result ? "fa-check" : "fa-xmark";
                const feedbackColor = result ? "text-success" : "text-danger";

                iconEl.classList.replace(originalClass, feedbackClass);
                iconEl.classList.add(feedbackColor);

                // After delay, revert icon and close menu
                setTimeout(() => {
                    if (menu.parentElement) {
                        iconEl.classList.replace(feedbackClass, originalClass);
                        iconEl.classList.remove(feedbackColor);
                        closeActiveMenu();
                    }
                }, 2000);
            } else {
                closeActiveMenu();
            }
        };

        menu.appendChild(btn);
    });

    return menu;
}

/**
 * Global function to close the active menu
 */
export function closeActiveMenu() {
    if (activeDropdownMenu) {
        activeDropdownMenu.remove();
        activeDropdownMenu = null;
    }
}

// Close menu if user clicks anywhere else
document.addEventListener("click", (e) => {
    if (activeDropdownMenu && !activeDropdownMenu.contains(e.target)) {
        closeActiveMenu();
    }
});
