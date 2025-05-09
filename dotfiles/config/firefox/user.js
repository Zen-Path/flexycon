// {{@@ header() @@}}

// Mirror the structure from 'about:preferences'

// = General =

// == General ==

// === Startup ===

// Open previous windows and tabs
// 0 : Blank Page
// 1 : Home Page
// 2 : Last Session
// 3: Home Page or Last Session
user_pref("browser.startup.page", 3);

// Always check if Firefox is your default browser
user_pref("browser.shell.checkDefaultBrowser", false);

// === Import Browser Data ===

// === Tabs ===

// Ctrl+Tab cycles through tabs in recently used order
user_pref("browser.ctrlTab.sortByRecentlyUsed", true);

// Open links in tabs instead of new windows
user_pref("browser.link.open_newwindow", true);

// Warn you when opening multiple tabs might slow down Firefox
user_pref("browser.tabs.warnOnOpen", true);

// When you open a link in a new tab, load it in the background
user_pref("browser.tabs.loadInBackground", true);

// Confirm before closing multiple tabs
user_pref("browser.tabs.warnOnClose", false);

// Confirm before quitting with Ctrl+Q
user_pref("browser.warnOnQuitShortcut", false);

// Show an image preview when you hover on a tab
user_pref("browser.tabs.hoverPreview.showThumbnails", true);

// Enable Container Tabs
user_pref("privacy.userContext.enabled", false);

// == Language and Appearance ==

// === Website appearance ===

// Color scheme
// 0 : dark
// 1 : light
// 2 : auto
user_pref("layout.css.prefers-color-scheme.content-override", 0);

// === Colors ===

// === Fonts ===

// Allow pages to choose their own fonts
// {%@@ if _dotfile_key == "f_firefox_user_front_end" @@%}

user_pref("browser.display.use_document_fonts", 1);
// {%@@ else @@%}

user_pref("browser.display.use_document_fonts", 0);
// {%@@ endif @@%}

// Fonts selection
user_pref("font.name.monospace.x-western", "Menlo");
user_pref("font.name.sans-serif.x-western", "Menlo");
user_pref("font.name.serif.x-western", "Menlo");

// === Zoom ===

// === Language ==

// Use your operating system settings to format dates, times, numbers, and measurements
user_pref("intl.regional_prefs.use_os_locales", false);

// Check your spelling as you type
user_pref("layout.spellcheckDefault", true);

// === Translations ===

// == Files and Applications ==

// === Downloads ===

// Use the download directory instead of always asking where to save files
user_pref("browser.download.useDownloadDir", true);

// === Applications ===

// What should Firefox do with other files?
user_pref("browser.download.always_ask_before_handling_new_types", false);

// === Digital Rights Management (DRM) Content ===

// Play DRM-controlled content
user_pref("media.eme.enabled", true);

// == Firefox Updates ==

// == Performance ==

// Use recommended performance settings
user_pref("browser.preferences.defaultPerformanceSettings.enabled", true);

// Use hardware acceleration when available
user_pref("layers.acceleration.disabled", false);

// == Browsing ==

// Use autoscrolling. Enabled with a middle mouse click
user_pref("general.autoScroll", true);

// Use smooth scrolling. You scroll by pixel instead of line height
// See: https://support.mozilla.org/en-US/questions/1346218
user_pref("general.smoothScroll", true);

// Always show scrollbars
user_pref("widget.gtk.overlay-scrollbars.enabled", true);

// Always use the cursor keys to navigate within pages
user_pref("accessibility.browsewithcaret", false);

// Always underline links
// {%@@ if _dotfile_key == "f_firefox_user_front_end" @@%}

user_pref("layout.css.always_underline_links", "false");
// {%@@ else @@%}

user_pref("layout.css.always_underline_links", "true");
// {%@@ endif @@%}

// Search for text when you start typing
user_pref("accessibility.typeaheadfind", false);

// Enable Picture-in-Picture video controls
user_pref("media.videocontrols.picture-in-picture.video-toggle.enabled", true);

// Control media via keyboard, headset, or virtual interface
user_pref("media.hardwaremediakeys.enabled", true);

// Recommend extensions as you browse
user_pref(
    "browser.newtabpage.activity-stream.asrouter.userprefs.cfr.addons",
    false
);

// Recommend features as you browse
user_pref(
    "browser.newtabpage.activity-stream.asrouter.userprefs.cfr.features",
    false
);

// == Network Settings ==

// = Home =

// == Home ==

// === New Windows and Tabs ===

// Homepage and new windows
user_pref("browser.startup.homepage", "chrome://browser/content/blanktab.html");

// New tabs
user_pref("browser.newtabpage.enabled", false);

// === Firefox Home Content ===

// Web Search
user_pref("browser.newtabpage.activity-stream.showSearch", false);

// Shortcuts
user_pref("browser.newtabpage.activity-stream.feeds.topsites", false);

// Sponsored shortcuts
user_pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);

// Recent activity
user_pref("browser.newtabpage.activity-stream.feeds.section.highlights", false);

// Visited pages
user_pref(
    "browser.newtabpage.activity-stream.section.highlights.includeVisited",
    false
);

// Bookmarks
user_pref(
    "browser.newtabpage.activity-stream.section.highlights.includeBookmarks",
    false
);

// Most recent download
user_pref(
    "browser.newtabpage.activity-stream.section.highlights.includeDownloads",
    false
);

// Pages saved to Pocket
user_pref(
    "browser.newtabpage.activity-stream.section.highlights.includePocket",
    false
);

// = Search =

// == Search ==

// === Search Suggestions ===

// Show search suggestions ahead of browsing history in address bar results
user_pref("browser.urlbar.showSearchSuggestionsFirst", false);

// Show search suggestions in Private Windows
user_pref("browser.search.suggest.enabled.private", false);

// Show trending search suggestions
user_pref("browser.urlbar.suggest.trending", false);

// Show recent searches
user_pref("browser.urlbar.suggest.recentsearches", true);

// === Address Bar ===

// Browsing history
user_pref("browser.urlbar.suggest.history", true);

// Bookmarks
user_pref("browser.urlbar.suggest.bookmark", true);

// Clipboard
user_pref("browser.urlbar.suggest.clipboard", true);

// Open tabs
user_pref("browser.urlbar.suggest.openpage", true);

// Shortcuts
user_pref("browser.urlbar.suggest.topsites", true); // [FF78+]

// Search engines
user_pref("browser.urlbar.suggest.engines", false);

// Quick actions
user_pref("browser.urlbar.suggest.quickactions", false);

// Suggestions from Firefox
user_pref("browser.urlbar.suggest.quicksuggest.nonsponsored", false);

// Suggestions from sponsors
user_pref("browser.urlbar.suggest.quicksuggest.sponsored", false);

// === Search Shortcuts ===

// = Privacy & Security

// == Browser Privacy ==

// === Enhanced Tracking Protection ===

// Choose which trackers and scripts to block
user_pref("browser.contentblocking.category", "custom");

// Cookies
// 0 : Don't block
// 1 : All cross-site cookies (may cause websites to break)
// 2 : All cookies (will cause websites to break)
// 3 : Cookies from unvisited websites
// 4 : Cross-site tracking cookies
// 5 : Cross-site tracking cookies, and isolate other cross-site cookies
user_pref("network.cookie.cookieBehavior", 5);

// Tracking content
user_pref("privacy.trackingprotection.emailtracking.enabled", true);
user_pref("privacy.trackingprotection.enabled", true);
user_pref("privacy.trackingprotection.socialtracking.enabled", true);

// Cryptominers
user_pref("privacy.trackingprotection.cryptomining.enabled", true);

// Known fingerprinters
user_pref("privacy.trackingprotection.fingerprinting.enabled", true);

// Suspected fingerprinters
user_pref("privacy.fingerprintingProtection", true);

// === Website Privacy Preferences ===

// Tell websites not to sell or share my data
user_pref("privacy.globalprivacycontrol.enabled", true);

// Send websites a “Do Not Track” request
user_pref("privacy.donottrackheader.enabled", true);

// === Cookies and Site Data ===

// Automatically refuse cookie banners
user_pref("cookiebanners.service.mode.privateBrowsing", false);

// Delete cache when Firefox is closed
user_pref("privacy.clearOnShutdown_v2.cache", false);

// Delete cookies when Firefox is closed
user_pref("privacy.clearOnShutdown_v2.cookiesAndStorage", false);

// Delete history, form data and downloads when Firefox is closed
user_pref("privacy.clearOnShutdown_v2.historyFormDataAndDownloads", false);

// === Passwords ===

// Ask to save passwords
user_pref("signon.rememberSignons", false);

// Fill usernames and passwords automatically
user_pref("signon.autofillForms", false);

// Suggest strong passwords
user_pref("signon.generation.enabled", false);

// Suggest Firefox Relay email masks to protect your email address
// user_pref("null", false);

// Show alerts about passwords for breached websites
user_pref("signon.management.page.breach-alerts.enabled", false);

// Use a Primary Password
// user_pref("null", false);

// === History ===

// Use custom settings for history
user_pref("privacy.history.custom", true);

// Always use private browsing mode
user_pref("browser.privatebrowsing.autostart", false);

// Remember browsing and download history
user_pref("places.history.enabled", true);

// Remember search and form history
user_pref("browser.formfill.enable", true);

// Clear history when Firefox closes
user_pref("privacy.sanitize.sanitizeOnShutdown", false);

// == Permissions ==

// Block pop-up windows
user_pref("dom.disable_open_during_load", true);

// Warn you when websites try to install add-ons
user_pref("xpinstall.whitelist.required", true);

// == Firefox Data Collection and Use ==

// Allow Firefox to send technical and interaction data to Mozilla
user_pref("datareporting.healthreport.uploadEnabled", false);

// Allow Firefox to make personalized extension recommendations
user_pref("browser.discovery.enabled", false);

// Allow Firefox to install and run studies
user_pref("app.shield.optoutstudies.enabled", false);

// Allow Firefox to send backlogged crash reports on your behalf
user_pref("browser.crashReports.unsubmittedCheck.autoSubmit2", false);

// == Website Advertising Preferences ==

// Allow websites to perform privacy-preserving ad measurement
user_pref("dom.private-attribution.submission.enabled", false);

// == Security ==

// === Deceptive Content and Dangerous Software Protection ===

// Block dangerous and deceptive content
// user_pref("null", false);

// Block dangerous downloads
// user_pref("null", false);

// Warn you about unwanted and uncommon software
// user_pref("null", false);

// === Certificates ===

// Query OCSP responder servers to confirm the current validity of certificates
user_pref("security.OCSP.enabled", true);

// === HTTPS-Only Mode ===

// Enable HTTPS-Only Mode in all windows
user_pref("dom.security.https_only_mode", true);

// == DNS over HTTPS ==

// === Enable DNS over HTTPS using: ===

// Protection
// 0 : Default Protection
// 1 : Off
// 2 : Increased Protection
// 3 : Max Protection
user_pref("network.trr.mode", 3);

// Choose provider:
user_pref("network.trr.uri", "https://mozilla.cloudflare-dns.com/dns-query");

// = Misc =

// Show the "Proceed with caution" warning on 'about:config'
user_pref("browser.aboutConfig.showWarning", false);

// Enable custom userChrome.css:
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

// Enable the pocket feature
user_pref("extensions.pocket.enabled", false);

// Enable the Firefox Sync feature
user_pref("identity.fxaccounts.enabled", true);

// Focus on the tags field when editing a bookmark
user_pref("browser.bookmarks.editDialog.firstEditField", "tagsField");

// Control when the context menu (right-click menu) is shown in relation
// to the mouse button action
// true : display context menu after the button is released
// false : display context menu as soon as the button is pressed
user_pref("ui.context_menus.after_mouseup", true);

// Control how and when the Referer header is sent for cross-origin requests
user_pref("network.http.referer.XOriginPolicy", 0);

// Enable search keywords
user_pref("keyword.enabled", true);

// Enable push notifications
user_pref("dom.push.enabled", true);

// Close the window when the last tab is closed
user_pref("browser.tabs.closeWindowWithLastTab", false);

// Auto-hide the download icon from the toolbar
user_pref("browser.download.autohideButton", false);

// Show the bookmarks bar
// - always
// - never
// - newtab
user_pref("browser.toolbars.bookmarks.visibility", "always");

// Theme
user_pref("extensions.activeThemeID", "firefox-compact-dark@mozilla.org");

// Devtools

// Enable browser chrome and add-on debugging toolboxes
user_pref("devtools.chrome.enabled", true);

// Enable remote debugging
user_pref("devtools.debugger.remote-enabled", true);

// Tab size
user_pref("devtools.editor.tabsize", 4);
