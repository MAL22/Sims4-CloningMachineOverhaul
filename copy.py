from Utilities import copy_module
from settings import *

root = os.path.join('__file__')
copy_module(root_path, src_path, dev_path)
