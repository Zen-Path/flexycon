-- Enable to manage files across sessions.
require("session"):setup {
	sync_yanked = true,
}

-- Add a full border around the main content.
require("full-border"):setup {
	-- Available values: ui.Border.PLAIN, ui.Border.ROUNDED
	type = ui.Border.ROUNDED,
}

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
