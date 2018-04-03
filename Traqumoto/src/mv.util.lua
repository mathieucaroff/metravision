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

return util