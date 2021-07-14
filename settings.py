import os

creator_name = 'MAL22'
mod_name = 'Cloning Machine Overhaul'

game_folder = os.path.join('C:', os.sep, 'Program Files (x86)', 'Games', 'The Sims 4')
mods_folder = os.path.expanduser(os.path.join('~', 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods'))

# Folder within the project where source code is stored
src_folder = 'src'

# Folder within the project where packaged builds are stored
build_folder = 'build'

# Folder within this project where asset files (package, XML tuning, images, etc.) are stored
assets_folder = 'assets'

# Temporary folder used to contain source files while the project is being compiled and packaged
temp_folder = 'temp'

# root folder of the project
root_path = os.path.dirname(os.path.realpath('__file__'))
print(root_path)

# /////////////////////////////////////////////////////////////////////////////
# full paths to the various folders configured above
src_path = os.path.join(root_path, src_folder)
build_path = os.path.join(root_path, build_folder)
assets_path = os.path.join(root_path, assets_folder)
temp_path = os.path.join(root_path, temp_folder)
dev_path = os.path.join(mods_folder, '!!modding', 'Scripts')
