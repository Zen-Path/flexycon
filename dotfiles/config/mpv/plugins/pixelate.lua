local mp = require("mp")

-- Configuration
local pixel_size = 8 -- Initial block size (higher = more pixelated)
local step = 2 -- How much to change block size per hotkey press
local min_pixel_size = 2 -- Minimum pixel size
local max_pixel_size = 64 -- Maximum pixel size

local active = false

local function apply_pixelation()
    if not active then
        return
    end

    -- Uses FFmpeg's scale filter to downscale then upscale (nearest neighbor), creating pixelation
    local filter = string.format(
        "lavfi=[scale=iw/%d:ih/%d:flags=neighbor,scale=iw*%d:ih*%d:flags=neighbor]",
        pixel_size,
        pixel_size,
        pixel_size,
        pixel_size
    )

    -- Dynamic replacement (@pixelate label replaces existing filter without flickering)
    mp.commandv("vf", "add", "@pixelate:" .. filter)
end

local function toggle_pixelate()
    if active then
        mp.commandv("vf", "remove", "@pixelate")
        active = false
        mp.osd_message("Pixelation: OFF")
    else
        active = true
        apply_pixelation()
        mp.osd_message("Pixelation: ON (" .. pixel_size .. "px)")
    end
end

local function increase_pixelation()
    if not active then
        return
    end

    if pixel_size < max_pixel_size then
        pixel_size = pixel_size + step
        apply_pixelation()
        mp.osd_message("Pixelation: " .. pixel_size .. "px")
    end
end

local function decrease_pixelation()
    if not active then
        return
    end

    if pixel_size > min_pixel_size then
        pixel_size = math.max(min_pixel_size, pixel_size - step)
        apply_pixelation()
        mp.osd_message("Pixelation: " .. pixel_size .. "px")
    end
end

-- Key bindings
mp.add_key_binding("alt+p", "toggle_pixelate", toggle_pixelate)
mp.add_key_binding("ctrl+=", "increase_pixelation", increase_pixelation)
mp.add_key_binding("ctrl+-", "decrease_pixelation", decrease_pixelation)
