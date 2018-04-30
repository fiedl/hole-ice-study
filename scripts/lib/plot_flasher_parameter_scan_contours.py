#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/57#issuecomment-385347525

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

flasher_data_file = "~/icecube/flasher-data/oux.63_30"
flasher_data = pandas.read_csv(flasher_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"])

import os
import glob2

simulation_data_folder = "~/hole-ice-study/results/flasher_parameter_scan"
simulation_data_files = list(glob2.glob(os.path.join(simulation_data_folder, "./**/hits.txt")))

for simulation_data_file in simulation_data_files:
  simulation_data = pandas.read_csv(simulation_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"], header = 1)
  simulation_options_file = os.path.join(os.path.dirname(simulation_data_file), "options.json")

