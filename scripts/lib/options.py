#!/usr/bin/env python

# Usage
#
#     import options
#
#     simulation_options = options.read(data_dir)
#     print simulation_options["brightness"]

import os
import json

def options_file(data_dir):
  return os.path.join(data_dir, "options.json")

def read(data_dir):
  return json.load(open(options_file(data_dir)))

def scaling(data_dir):
  options = read(data_dir)
  return 1.0 * options.get("brightness", 127) * options.get("width", 127) * options.get("thinning", 1.0)

def write(data_dir, options):
  with open(options_file(data_dir), "w") as outfile:
    json.dump(options, outfile)

def append(data_dir, new_options):
  opts = read(data_dir)
  opts.update(new_options)
  write(data_dir, opts)
