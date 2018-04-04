local util = {}

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
    if util.fileExists(filename) then
    else
        util.printFileMissingMessage(filename)
        util.printTRM("Exiting.")
        os.exit(1)
    end
end

function util.printTRM_table (tbl, indent)
    if not indent then indent = 0 end
    for key, val in pairs(tbl) do
        formattingKey = string.rep("  ", indent) .. key .. ":"
        if type(val) == "table" then
            printTRM(formattingKey)
            util.printTRM_table(val, indent + 2)
        else
            printTRM(formattingKey .. " " .. val)
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

return util