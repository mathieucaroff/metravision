require("solve-environement")

util = require("mv.util")
config = require("../mv.config")

-- External libraries
require 'torch'
require 'nn'
cv = require 'cv'	-- Utilisation d'OpenCV

-- mv.util.lua
printTRM = util.printTRM

-- ../mv.config.lua
-- cr = config.creationReseau