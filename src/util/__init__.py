# pylint: disable=wildcard-import
from util.contexttool import *
from util.decorator import *
from util.dotdict import *
from util.geometric import *
from util.long import *
from util.short import *

class DeveloperInterruption(Exception):
    pass

developerMode = "Set by main to the value given in the yaml configuration file."