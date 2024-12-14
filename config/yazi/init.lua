-- Allow for lf-like ability to manage files across instances.
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
