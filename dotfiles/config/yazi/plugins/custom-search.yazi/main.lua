local function prompt()
    return ya.input({
        title = "Custom search:",
        position = { "center", w = 50 },
        realtime = false,
        debounce = 0.1,
    })
end

local function entry()
    local value, event = prompt()

    local search_value, search_opts = value:match('^"(.-)"%s*(.*)$')

    if search_value then
        ya.dbg("Search Value:", search_value)
        ya.dbg("Search Options:", search_opts)
    else
        -- If no quoted string is found, treat the whole input as search_opts
        search_opts = nil
        search_value = value
        ya.dbg("Search Value: nil")
        ya.dbg("Search Options:", search_opts)
    end

    ya.manager_emit(
        "search_do",
        { search_value, via = "fd", args = search_opts }
    )
end

return { entry = entry }
