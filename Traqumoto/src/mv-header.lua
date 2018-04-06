-- # Metravision Lua Header File # --

-- Globals:
-- util, config, cv, printTRM

util = require 'mv-util'

config = require '../mv-config'

require 'mv-setup-environnement'

-- External libraries
require 'torch'
require 'nn'
cv = require 'cv'	-- Utilisation d'OpenCV

-- mv.util.lua
printTRM = util.printTRM

printTRM(" <Configuration>")
util.printTRM_table(config)