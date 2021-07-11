from Utilities import copy_module
from settings import *

root = os.path.dirname(os.path.realpath('__file__'))
copy_module(root, mods_folder)
