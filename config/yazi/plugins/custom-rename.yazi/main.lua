function utility_exists(utility)
    -- Check if the OS is Windows (Windows path separator is '\')
    local is_windows = package.config:sub(1,1) == '\\'
    local command

    if is_windows then
        -- 'where' is used on Windows
        command = "where " .. utility .. " > nul 2>&1"
    else
        -- For Unix-like systems
        command = "command -v " .. utility .. " > /dev/null 2>&1"
    end

    -- Run the command and capture the results.
    local result, exit_type, exit_code = os.execute(command)

    -- If the result is a number (Lua 5.1), check if it equals 0.
    if type(result) == "number" then
        return result == 0
    else
        -- For Lua 5.2 and later, result is a boolean. Also check the exit code.
        return result and exit_code == 0
    end
end

local function entry(_, job)
    if utility_exists("vidir") then
        ya.dbg("vidir is available.")

        if job.args[1] == "full-path" then
            ya.mgr_emit("shell", { 'vidir -- \"$@\"', block = true })
        else
            ya.mgr_emit("shell", { 'vidir -- $(basename -a -- \"$@\")', block = true })
        end
    else
        ya.dbg("vidir is not available.")

        ya.mgr_emit("rename", { bulk = true })
    end
end

return { entry = entry }
