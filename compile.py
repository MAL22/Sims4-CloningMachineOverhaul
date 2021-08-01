from Utilities import compile_module, copy_packages
from settings import *

compile_module(creator_name, mod_name, root_path, src_path, temp_path, build_path, mods_folder)
copy_packages(assets_path, dev_path)