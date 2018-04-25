#!/usr/bin/env python

import sys
import pandas

import os
import glob2

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np

import json
from dateutil import parser

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

base_paths = sys.argv[1:]

options_files = []
for base_path in base_paths:
  options_files = options_files + list(glob2.glob(os.path.join(base_path, "./**/options.json")))

pulse_widths = []
simulation_times = []
simulation_times_minutes = []
simulation_times_hours = []
simulation_numbers_of_hits = []
simulation_overscaling_factors = []

for options_file in options_files:
  options = json.load(open(options_file))

  pulse_widths.append(options["flasher"]["width"])
  duration_in_seconds = (parser.parse(options["finished_at"]) - parser.parse(options["started_at"])).seconds
  simulation_times.append(duration_in_seconds)
  simulation_times_minutes.append(duration_in_seconds / 60)
  simulation_times_hours.append(duration_in_seconds / 3600)

  hits_file = os.path.join(os.path.dirname(options_file), "hits.txt")
  simulation_data = pandas.read_csv(hits_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"], header = 1)
  total_number_of_hits_in_detector = simulation_data["charge"].sum()
  simulation_numbers_of_hits.append(total_number_of_hits_in_detector)

  data_total_number_of_hits = 72039 # https://github.com/fiedl/hole-ice-study/issues/57#issuecomment-383990496
  overscaling_factor = total_number_of_hits_in_detector * 1.0 / data_total_number_of_hits
  simulation_overscaling_factors.append(overscaling_factor)

# prepare canvas
fig, [ax0, ax1, ax2, ax3] = plt.subplots(4, 1, facecolor="white")

ax0.plot(pulse_widths, simulation_times_hours, "o")
ax0.set_xlabel("Flasher pulse width setting")
ax0.set_ylabel("Simulation time [hours]")
ax0.set_title("Flasher simulation performance")

ax1.plot(pulse_widths, simulation_numbers_of_hits, "o")
ax1.set_xlabel("Flasher pulse width setting")
ax1.set_ylabel("Total number of hits in detector")

ax2.plot(simulation_numbers_of_hits, simulation_times_hours, "ro")
ax2.set_xlabel("Total number of hits in detector")
ax2.set_ylabel("Simulation time [hours]")

ax3.plot(simulation_overscaling_factors, simulation_times_hours, "ro")
ax3.set_xlabel("Simulation vs. data overscaling factor")
ax3.set_ylabel("Simulation time [hours]")

plt.show()
