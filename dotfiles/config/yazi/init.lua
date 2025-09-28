-- Enable to manage files across sessions.
require("session"):setup({
    sync_yanked = true,
})

-- Add a full border around the main content.
require("full-border"):setup({
    -- Available values: ui.Border.PLAIN, ui.Border.ROUNDED
    type = ui.Border.ROUNDED,
})

-- Show the status of Git file changes as linemode in the file list.
require("git"):setup()

-- Docs: https://yazi-rs.github.io/docs/tips#symlink-in-status
function Status:name()
    local h = self._current.hovered
    if not h then
        return ""
    end

    local linked = ""
    if h.link_to ~= nil then
        linked = " -> " .. tostring(h.link_to)
    end
    return ui.Line(" " .. h.name .. linked)
end

-- Enable the starship integration
require("starship"):setup({
    -- Hide flags (such as filter, find and search). This is recommended for starship themes which
    -- are intended to go across the entire width of the terminal.
    hide_flags = false, -- Default: false
    -- Whether to place flags after the starship prompt. False means the flags will be placed before the prompt.
    flags_after_prompt = true, -- Default: true
    -- Custom starship configuration file to use
    config_file = "~/.config/starship/yazi_cfg.toml", -- Default: nil
})
