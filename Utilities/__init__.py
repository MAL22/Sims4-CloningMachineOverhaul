from zipfile import PyZipFile, ZIP_STORED

import shutil

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


def compile_module(creator_name, mod_name, root_path, src_path, temp_path, build_path, mods_folder):
    mod_name = creator_name + '_' + mod_name
    mod_archive = mod_name + '.ts4script'

    exclude_file = {'copy.py', 'compile.py', f"{mod_archive}"}
    exclude_folder = {'__pycache__', 'temp', 'assets', 'EA'}

    print('Scanning \'{}\'...'.format(mod_name.replace(creator_name + '_', '')))
    print('Ignored file{}: {}'.format('s' if len(exclude_file) > 1 else '', ', '.join(exclude_file)))
    print('Ignored folder{}: {}'.format('s' if len(exclude_folder) > 1 else '', ', '.join(exclude_folder)))

    if os.path.exists(os.path.join(mods_folder, mod_archive)):
        os.remove(os.path.join(mods_folder, mod_archive))
        print('Removed \'{}\' from mods folder'.format(mod_archive))

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
        print('Created temporary directory')

    if not os.path.exists(build_path):
        os.makedirs(build_path)
        print('Created build folder in project folder')
    elif os.path.exists(os.path.join(src_path, mod_archive)):
        os.remove(os.path.join(src_path, mod_archive))
        print('Removed \'{}\' from project folder'.format(mod_archive))

    zip_file = PyZipFile(os.path.join(build_path, mod_archive), mode='w', compression=ZIP_STORED, allowZip64=True, optimize=2)

    for folder, subs, files in os.walk(src_path):
        rel_module_path = ''.join(folder.rsplit(root_path))
        module_folder = os.path.join(temp_path, *rel_module_path[1:].split('\\')[1:])

        if not os.path.exists(module_folder):
            os.makedirs(module_folder)

        subs[:] = [sub for sub in subs if sub not in exclude_folder]
        files[:] = [file for file in files if file not in exclude_file]
        if len(files) > 0:
            print('Found {} script(s): {}'.format(len(files), ', '.join(files)))
        for file in files:
            shutil.copyfile(os.path.join(folder, file), os.path.join(module_folder, file))

    print('Packaging \'{}\'...'.format(mod_archive))
    for folder, subs, files in os.walk(temp_path):
        subs[:] = [sub for sub in subs if sub not in exclude_folder]
        for file in files:
            zip_file.writepy(os.path.join(folder, file), os.path.relpath(folder, 'temp'))

    zip_file.close()

    response = ''
    while response not in ['y', 'n']:
        response = input('Copy \'{}\' to the Sims 4 mods folder? (Y/N): '.format(mod_archive)).casefold()
    if response == 'y':
        shutil.copyfile(os.path.join(build_path, mod_archive), os.path.join(mods_folder, mod_archive))

    shutil.rmtree(temp_path)
    print('Packaging complete!')


def copy_module(root_path, src_path, dev_path):
    exclude = {'__pycache__', 'EA'}

    for folder, subs, files in os.walk(src_path):
        subs[:] = [sub for sub in subs if sub not in exclude]
        rel_module_path = ''.join(folder.rsplit(root_path))
        module_path = os.path.join(dev_path, *rel_module_path[1:].split('\\')[1:])
        for file in files:
            fsrc = os.path.join(folder, file)
            fdst = os.path.join(module_path, file)
            print('\t' + fsrc + '\n\t' + fdst)
            shutil.copyfile(fsrc, fdst)
