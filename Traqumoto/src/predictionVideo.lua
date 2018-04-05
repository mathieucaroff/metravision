--[[ Logiciel
Metravision]]

--[[ Description du ficher
]]

--lfs = require 'lfs'
-- printTRM(lfs.currentdir())
-- sourceLocation = dirname(lfs.currentdir() .. "/" .. arg[0]) .. "?.lua;"
-- printTRM(sourceLocation)
-- lfs.chdir(herePath)
-- package.path = package.path .. (";" .. sourceLocation .. "./?.lua;")

package.path = package.path .. ";src/?.lua"
require 'mv-header'

dofile("prediction.lua") -- Execute le fichier prediction.lua
