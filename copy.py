from Utilities import copy_module, copy_packages, find_package_files
from settings import *

copy_module(root_path, src_path, dev_path, dev_scripts_path)
copy_packages(assets_path, dev_path)
