#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import shutil
import subprocess
import sys

# Map of keyboard layouts with their full names
layout_full_names = {
    "us": "English (US)",
    "ro": "Romanian",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "cz": "Czech",
    "ca": "Canadian",
    # Add more layouts as needed
}


def get_current_layout():
    """Fetch the current keyboard layout."""
    try:
        result = subprocess.run(
            ["setxkbmap", "-query"], capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("layout:"):
                return line.split()[1]
    except subprocess.CalledProcessError:
        print("Error: Unable to get current layout.")
        sys.exit(1)


def get_available_layouts():
    """Get the available keyboard layouts using localectl."""
    try:
        result = subprocess.run(
            ["localectl", "list-x11-keymap-layouts"],
            capture_output=True,
            text=True,
            check=True,
        )
        layouts = result.stdout.splitlines()
        return layouts
    except subprocess.CalledProcessError:
        print("Error: Unable to list x11 keymap layouts.")
        sys.exit(1)


def format_layouts(available_layouts, layout_full_names):
    """Combine the shorthand and long names if available."""
    formatted_layouts = []
    for layout in available_layouts:
        if layout in layout_full_names:
            formatted_layouts.append(f"{layout} - {layout_full_names[layout]}")
        else:
            formatted_layouts.append(layout)
    return formatted_layouts


def prompt_layout(formatted_layouts, current_layout):
    """Prompt the user to select a layout, displaying the current layout."""
    dmenu_prompt = f"Select Keyboard Layout (current: {current_layout}):"
    try:
        result = subprocess.run(
            ["dmenu", "-i", "-l", "15", "-p", dmenu_prompt],
            input="\n".join(formatted_layouts),
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: dmenu failed to run.")
        sys.exit(1)


def restart_remapd():
    """Restart the remapd service if it's available."""
    if shutil.which("remapd"):
        try:
            subprocess.run(["killall", "remapd"], check=True)
            print("remapd killed successfully.")
            # Restart remapd if necessary (customize based on how you restart it)
            subprocess.Popen(["remapd"])
            print("remapd restarted successfully.")
        except subprocess.CalledProcessError:
            print("Failed to restart remapd.")
    else:
        print("remapd is not available in this environment.")


def set_keyboard_layout(layout):
    """Set the chosen keyboard layout."""
    try:
        subprocess.run(["setxkbmap", layout], check=True)
        subprocess.run(["notify-send", f"Keyboard layout changed to {layout}"])
    except subprocess.CalledProcessError:
        print(f"Error: Unable to set layout to {layout}.")
        sys.exit(1)


def main():
    current_layout = get_current_layout()
    available_layouts = get_available_layouts()

    formatted_layouts = format_layouts(available_layouts, layout_full_names)
    chosen_layout = prompt_layout(formatted_layouts, current_layout)

    if chosen_layout:
        layout_code = chosen_layout.split(" - ")[0]
        if layout_code in available_layouts:
            set_keyboard_layout(layout_code)
            print(f"Keyboard layout set to: {layout_code}")
            restart_remapd()  # Call restart_remapd from here
        else:
            print("Invalid layout selected.")
    else:
        print("No layout chosen.")


if __name__ == "__main__":
    main()
