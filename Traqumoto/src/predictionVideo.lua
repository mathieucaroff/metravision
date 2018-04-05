--[[ Logiciel
Metravision]]

--[[ Description du ficher
]]

lfs = require 'lfs'

printTRM("TMR]" .. lfs.currentdir())

function dirname(path)
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

sourceLocation = dirname(lfs.currentdir() .. "/" .. arg[0]) .. "?.lua;"

printTRM(sourceLocation)

lfs.chdir(herePath)

package.path = package.path .. (";" .. sourceLocation .. "./?.lua;")

require 'mv-header'

dofile("prediction.lua") -- Execute le fichier prediction.lua
