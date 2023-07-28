# BUILD : python build.py bdist_msi
# UUID : import uuid str(uuid.uuid3(uuid.NAMESPACE_DNS, 'pyjoinlogoscpencode.hsa12.net')).upper()

import sys
import distutils
from cx_Freeze import setup, Executable

import values
EXE_FILE_NAME = values.EXE_FILE_NAME
EXE_VER = values.EXE_VER
EXE_NAME_VER = values.EXE_NAME_VER
EXE_NO_CUI = values.EXE_NO_CUI

#Application information
name = EXE_FILE_NAME
version = str(EXE_VER)
author = 'HsaS'
author_email = 'hsas@hsa12.net'
url = 'https://github.com/HsaSheep/pyJoinLogoScpEncode'
description = "Auto CM-Cut and Encode controller."
target_py = "main.py"
# Specify the GUID here (basically it should not be changed)
upgrade_code = '{6A8877F5-0088-3065-9876-E9C3CAF4A491}'
# For 64-bit Windows, switch the installation folder
# ProgramFiles(64)Folder seems to be replaced with the actual directory on the msi side
programfiles_dir = 'ProgramFiles64Folder' if distutils.util.get_platform() == 'win-amd64' else 'ProgramFilesFolder'

build_exe_options = {
    # 'packages': ['os'],
    # 'excludes': [''],
    # 'includes': [''],
    'include_files': ['inc_dir/'],
    # 'include_msvcr': True,  # Since it uses PySide, it cannot be started unless Microsoft's C runtime is included.
    'zip_include_packages': '*',
    'zip_exclude_packages': '',
}

# bdist_Options to use with the msi command
bdist_msi_options = {
    'upgrade_code': upgrade_code,
    'add_to_path': False,
    'initial_target_dir': '[%s]\%s\%s' % (programfiles_dir, author, name)
}

options = {
    'build_exe': build_exe_options,
    'bdist_msi': bdist_msi_options
}

# exe information
# コンソール非表示 #
if (sys.platform == "win32") and (EXE_NO_CUI == "True"):
    base = "Win32GUI"
else:
    base = None
icon = 'inc_dir/icon.ico'

main_exe = Executable(
    target_py,
    target_name=name + ".exe",
    base=base,
    icon=icon,
    shortcut_name=EXE_FILE_NAME,
    shortcut_dir="ProgramMenuFolder",
)

setup(
    name=name,
    version=version,
    author=author,
    author_email=author_email,
    url=url,
    description=description,
    options=options,
    executables=[main_exe]
)