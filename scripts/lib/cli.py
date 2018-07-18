# Usage
#
#     import cli
#     for data_dir in cli.data_dirs():
#       # ...
#
#     ./test_script.py ~/data_root_folder1 ~/data_root_folder2

import sys
import os
import glob2

def data_root_folders():
  return sys.argv[1:]

def options_files():
  options_files = []
  for data_root_folder in data_root_folders():
    options_files += glob2.glob(os.path.join(data_root_folder, "./**/options.txt"))
  return options_files

def data_dirs():
  return list((os.path.dirname(options_file) for options_file in options_files()))
