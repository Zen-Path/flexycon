-- Helper: read a single env var from your login shell
local function getShellVar(varName, shellPath)
    shellPath = shellPath or "/bin/zsh"
    local cmd =
        string.format("%s -l -c 'printf %%s \"$%s\"'", shellPath, varName)
    local out, ok = hs.execute(cmd)
    if not ok or out == "" then
        return ""
    end
    return out:gsub("%s+$", "") -- trim any trailing newline/space
end

-- Helper: launch (or focus) an app by its macOS name, opening a new instance if already running
local function launchApp(appName)
    if hs.application.get(appName) then
        -- already running: open a fresh instance/window
        hs.execute(string.format('open -na "%s"', appName))
    else
        -- not running: focus or launch
        hs.application.launchOrFocus(appName)
    end
end

local function getBrowserAppName()
    local exec = getShellVar("BROWSER")
    local map = {
        firefox = "Firefox",
        ["google-chrome"] = "Google Chrome",
        safari = "Safari",
        edge = "Microsoft Edge",
    }

    if map[exec] == nil then
        hs.alert.show("⚠️ $BROWSER not set")
    end

    local app = map[exec] or exec
    return app
end

mods1 = { "command", "control" }
mods2 = { "command", "control", "shift" }

hs.hotkey.bind(mods1, "return", function()
    hs.application.launchOrFocus("kitty")
end)

-- Launch a web browser instance
hs.hotkey.bind(mods1, "W", function()
    local app = getBrowserAppName()
    launchApp(app)
end)

-- Open firefox's (Web browser) profile selector
hs.hotkey.bind(mods2, "W", function()
    hs.execute([[open -na "Firefox" --args -P]])
end)

-- Quit the front-most window
hs.hotkey.bind(mods1, "Q", function()
    local win = hs.window.frontmostWindow()
    win:close() -- equivalent to ⌘-W
    hs.alert.show(
        "Closed window: “" .. (win:title() or "<untitled>") .. "”"
    )
end)

-- Quit the front-most app
hs.hotkey.bind({ "ctrl", "cmd", "shift" }, "Q", function()
    local app = hs.application.frontmostApplication()
    local name = app:name()
    hs.alert.show("Killing “" .. name .. "”")
    -- Gentle terminate; use app:kill9() for SIGKILL if needed
    app:kill()
end)

-- Auto-reload on changes
hs.pathwatcher
    .new(os.getenv("HOME") .. "/.hammerspoon/init.lua", hs.reload)
    :start()
hs.alert.show("🔨 Hammerspoon config loaded")
