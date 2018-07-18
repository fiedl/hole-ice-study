#!/usr/bin/env python

import os
import glob2
import pandas

def flasher_hits(data_dir):
  data_files = list(glob2.glob(os.path.join(os.path.expanduser(data_dir), "./**/hits.txt")))
  return pandas.concat(map(lambda file: pandas.read_csv(file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"], header = 1), data_files))


import options

def scaling(data_dir):
  return options.scaling(data_dir)