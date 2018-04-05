util = {}

function util.printTRM(arg1, ...)
    text = tostring(arg1)
    -- first = text:sub(0, 1)
    if text:match("^[][(){}<>:| ]") then
        space = ""
    else
        space = " "
    end
    print("[TRM]" .. space .. text, ...)
end
local printTRM = util.printTRM

function util.fileExists(filename)
    local exists
    local file = io.open(filename)
    if file ~= nil then
        file:close()
        exists = true
    else
        exists = false
    end
    return exists
end

function util.printFileMissingMessage(filename)
    printTRM("File `" .. filename .. "` doesn't exist.")
end

function util.tellIfMissing(filename)
    if util.fileExists(filename) then
    else
        util.printFileMissingMessage(filename)
    end
end

function util.exitIfMissing(filename)
    if util.fileExists(assert(filename)) then
    else
        util.printFileMissingMessage(filename)
        util.printTRM("Exiting.")
        os.exit(1)
    end
end

function util.formatTypeValue (val)
    return string.format("(%s) %s", tostring(type(val)):sub(1, 3), tostring(val))
end

function util.sortedIpairs(tbl)
    local sortedKeys = {}
    -- populate the table that holds the keys
    for key in pairs(tbl) do table.insert(sortedKeys, key) end
    table.sort(sortedKeys)

    function tblIterator (_, index)
        key = sortedKeys[index]
        val = tbl[key]
        if key ~= nil then
            return index + 1, key, val
        else
            return nil
        end
    end

    return tblIterator, nil, 1
end

function util.printTRM_table(tbl, indent)
    if not indent then indent = 0 end
    for _, key, val in util.sortedIpairs(tbl) do
        if key == nil then key = "NILKEY" end
        if val == nil then val = "NILVAL" end
        formattingKey = string.rep("  ", indent) .. key .. ":"
        if type(val) == "table" then
            printTRM(formattingKey)
            util.printTRM_table(val, indent + 2)
        else
            printTRM(formattingKey .. " " .. util.formatTypeValue(val))
        end
    end
end

function util.nope ()
end

-- Run a command and get it's output
function util.capture(cmd, raw)
    local f = assert(io.popen(cmd, 'r'))
    local s = assert(f:read('*a'))
    f:close()
    if raw then return s end
    s = string.gsub(s, '^%s+', '')
    s = string.gsub(s, '%s+$', '') -- Remove trailing space
    s = string.gsub(s, '[\n\r]+', ' ') -- Remove newlines
    return s
end

function util.dirname(path)
    lastSlashPattern = "/[^/]*$" -- linux
    -- lastSlashPattern = "\\[^\\]*$" -- windows
    lastSlashIndex = path:find(lastSlashPattern)
    if lastSlashIndex ~= nil then
        dir = path:sub(1, lastSlashIndex)
    else
        dir = "./"
    end
    return dir
end

--[[
* Obtenir une vidéo de l'utilisateur.
]]
function util.getFile()
    local path = util.capture("bash -c 'zenity  --title=\"Select a video\" --file-selection' 2> /dev/null")
    return path
end

return util