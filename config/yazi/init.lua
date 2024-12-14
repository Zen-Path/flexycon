-- Allow for lf-like ability to manage files across instances.
require("session"):setup {
	sync_yanked = true,
}
