import pkgutil
import sys
from zipfile import PyZipFile, ZIP_STORED

import shutil
from pathlib import Path

import importlib
import importlib.util
import modulefinder
import list_imports

import io
from Utilities.unpyc3 import decompile
import fnmatch
import os


def decompile_dir(rootPath):
    pattern = '*.pyc'
    for root, dirs, files in os.walk(rootPath):
        for filename in fnmatch.filter(files, pattern):
            p = str(os.path.join(root, filename))
            try:
                py = decompile(p)
                with io.open(p.replace('.pyc', '.py'), 'w') as output_py:
                    for statement in py.statements:
                        output_py.write(str(statement) + '\r')
                print(p)
            except Exception as ex:
                print("FAILED to decompile %s" % p)


script_package_types = ['*.zip', '*.ts4script']


def extract_subfolder(root, filename, ea_folder):
    src = os.path.join(root, filename)
    dst = os.path.join(ea_folder, filename)
    if src != dst:
        shutil.copyfile(src, dst)
    zip = PyZipFile(dst)
    out_folder = os.path.join(ea_folder, os.path.splitext(filename)[0])
    zip.extractall(out_folder)
    decompile_dir(out_folder)
    pass


def extract_folder(ea_folder, gameplay_folder):
    for root, dirs, files in os.walk(gameplay_folder):
        for ext_filter in script_package_types:
            for filename in fnmatch.filter(files, ext_filter):
                extract_subfolder(root, filename, ea_folder)


def old_compile_module(creator_name, root, mods_folder, mod_name=None, use_creator_name=True):
    src = os.path.join(root, 'src')
    if not mod_name:
        mod_name=os.path.basename(os.path.normpath(os.path.dirname(os.path.realpath('__file__'))))

    if use_creator_name:
        mod_name = creator_name + '_' + mod_name
    ts4script = os.path.join(root, mod_name + '.ts4script')

    ts4script_mods = os.path.join(os.path.join(mods_folder), mod_name + '.ts4script')

    zf = PyZipFile(ts4script, mode='w', compression=ZIP_STORED, allowZip64=True, optimize=2)
    for folder, subs, files in os.walk(src):
        zf.writepy(folder)
    zf.close()
    shutil.copyfile(ts4script, ts4script_mods)


def compile_module(creator_name, root, mods_folder, mod_name=None):
    if not mod_name:
        mod_name = os.path.basename(os.path.normpath(os.path.dirname(os.path.realpath('__file__'))))

    mod_name = creator_name + '_' + mod_name
    mod_archive = mod_name + '.ts4script'

    src = root # os.path.join(root, 'src')
    temp_folder = os.path.join(root, 'temp')

    ts4script_mods = os.path.join(mods_folder, mod_archive)

    exclude_file = {'copy.py', 'compile.py', f"{mod_archive}"}
    exclude_folder = {'__pycache__', 'temp', 'package'}

    print('Scanning \'{}\'...'.format(mod_name.replace(creator_name + '_', '')))
    print('Ignoring file{}: {}'.format('s' if len(exclude_file) > 1 else '', ', '.join(exclude_file)))
    print('Ignoring folder{}: {}'.format('s' if len(exclude_folder) > 1 else '', ', '.join(exclude_folder)))

    if os.path.exists(os.path.join(src, mod_archive)):
        os.remove(os.path.join(src, mod_archive))
        print('Removed \'{}\' from project folder'.format(os.path.basename(mod_archive)))

    if os.path.exists(ts4script_mods):
        os.remove(ts4script_mods)
        print('Removed \'{}\' from mods folder'.format(os.path.basename(mod_archive)))

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
        print('Created temporary directory')

    zip_file = PyZipFile(os.path.join(src, mod_archive), mode='w', compression=ZIP_STORED, allowZip64=True, optimize=2)

    for folder, subs, files in os.walk(src):
        rel_module_path = ''.join(folder.rsplit(root))
        module_folder = os.path.join(temp_folder, *rel_module_path[1:].split('\\')[1:])

        if not os.path.exists(module_folder):
            os.makedirs(module_folder)

        subs[:] = [sub for sub in subs if sub not in exclude_folder]
        files[:] = [file for file in files if file not in exclude_file]
        if len(files) > 0:
            print('Found {} script(s): {}'.format(len(files), ', '.join(files)))
        for file in files:
            shutil.copyfile(os.path.join(folder, file), os.path.join(module_folder, file))
            # import_file_dependencies(module_folder, folder, file)

    print('Packaging \'{}\' and all dependencies...'.format(os.path.basename(ts4script_mods)))
    for folder, subs, files in os.walk(temp_folder):
        subs[:] = [sub for sub in subs if sub not in exclude_folder]
        for file in files:
            zip_file.writepy(os.path.join(folder, file), os.path.relpath(folder, 'temp'))

    zip_file.close()

    response = ''
    while response not in ['y', 'n']:
        response = input('Copy \'{}\' to the Sims 4 mods folder? (Y/N): '.format(os.path.basename(ts4script_mods))).casefold()

    if response == 'y':
        shutil.copyfile(os.path.join(src, mod_archive), ts4script_mods)

    shutil.rmtree(temp_folder)
    print('Packaging complete!')


def import_file_dependencies(temp, root, file):
    path = os.path.join(root, file)
    imports = [imp for imp in list_imports.get(path) if "m22lib" in imp]
    len_imports = len(imports)

    if len_imports > 0:
        print('Importing {} dependenc{} for \'{}\': {}'.format(len_imports, 'y' if len_imports == 1 else 'ies', file, ', '.join(imports)))
        mod_finder = modulefinder.ModuleFinder()
        mod_finder.run_script(path)

        for name, mod in mod_finder.modules.items():
            if name in imports:
                split_path = str(name).split('.')
                len_path = len(split_path)

                if len_path == 1:
                    continue

                dependency_filename = split_path[len_path - 1] + '.py'
                dependency_path = os.path.join(*split_path[:len_path - 1])

                workspace_folder = os.path.dirname(mod.__file__).replace(os.path.join(os.sep, dependency_path), '')

                if not os.path.exists(os.path.join(temp, dependency_path)):
                    os.makedirs(os.path.join(temp, dependency_path))

                temp_path = temp
                for folder, subs, files in os.walk(workspace_folder):
                    subs[:] = [sub for sub in subs if sub in [*split_path[:len_path - 1]]]
                    files[:] = [file for file in files if file == "__init__.py"]
                    for sub in subs:
                        temp_path = os.path.join(temp_path, sub)
                        if os.path.exists(os.path.join(folder, sub, '__init__.py')):
                            shutil.copyfile(os.path.join(folder, sub, '__init__.py'), os.path.join(temp_path, '__init__.py'))

                shutil.copyfile(mod.__file__, os.path.join(temp, dependency_path, dependency_filename))
                import_file_dependencies(temp, os.path.dirname(mod.__file__), dependency_filename)


def copy_module(root, mods_folder):
    src = os.path.join(root, 'src')

    py_scripts = os.path.join(mods_folder, '!!modding', 'Scripts')

    exclude = set(['__pycache__'])

    for folder, subs, files in os.walk(src):
        subs[:] = [sub for sub in subs if sub not in exclude]
        rel_module_path = ''.join(folder.rsplit(root))
        module_path = os.path.join(py_scripts, *rel_module_path[1:].split('\\')[1:])
        for file in files:
            fsrc = os.path.join(folder, file)
            fdst = os.path.join(module_path, file)
            print('\t' + fsrc + '\n\t' + fdst)
            shutil.copyfile(fsrc, fdst)
