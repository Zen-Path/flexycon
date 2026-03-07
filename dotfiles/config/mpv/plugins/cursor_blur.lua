local mp = require("mp")

-- Change this to make the blur box larger or smaller
local blur_radius = 100

local blur_active = false

function toggle_cursor_blur()
    if blur_active then
        mp.commandv("vf", "remove", "@cursor_blur")
        blur_active = false
        mp.osd_message("Cursor Blur: OFF")
        return
    end

    local mouse = mp.get_property_native("mouse-pos")
    if not mouse then
        return
    end

    local vw = mp.get_property_number("video-params/w")
    local vh = mp.get_property_number("video-params/h")
    local ww = mp.get_property_number("osd-width")
    local wh = mp.get_property_number("osd-height")

    if not vw or not vh or not ww or not wh then
        return
    end

    -- Calculate exact video coordinates accounting for black bars
    local window_ar = ww / wh
    local video_ar = vw / vh
    local disp_w, disp_h, x_off, y_off

    if window_ar > video_ar then
        disp_h = wh
        disp_w = wh * video_ar
        x_off = (ww - disp_w) / 2
        y_off = 0
    else
        disp_w = ww
        disp_h = ww / video_ar
        x_off = 0
        y_off = (wh - disp_h) / 2
    end

    local vid_x = (mouse.x - x_off) * (vw / disp_w)
    local vid_y = (mouse.y - y_off) * (vh / disp_h)

    -- Force even numbers for FFmpeg compatibility (prevents crashes on YUV videos)
    local x = math.floor((vid_x - blur_radius) / 2) * 2
    local y = math.floor((vid_y - blur_radius) / 2) * 2
    local w = math.floor((blur_radius * 2) / 2) * 2
    local h = math.floor((blur_radius * 2) / 2) * 2

    -- Clamp box to video edges
    if x < 0 then
        x = 0
    end
    if y < 0 then
        y = 0
    end
    if x + w > vw then
        w = math.floor((vw - x) / 2) * 2
    end
    if y + h > vh then
        h = math.floor((vh - y) / 2) * 2
    end

    if w > 0 and h > 0 then
        -- Uses the 'delogo' filter which is optimized for regional blurring
        local filter = string.format(
            "lavfi=[delogo=x=%d:y=%d:w=%d:h=%d:show=0]",
            x,
            y,
            w,
            h
        )
        mp.commandv("vf", "add", "@cursor_blur:" .. filter)
        blur_active = true
        mp.osd_message("Cursor Blur: ON")
    end
end

mp.add_key_binding("ctrl+b", "toggle_cursor_blur", toggle_cursor_blur)
