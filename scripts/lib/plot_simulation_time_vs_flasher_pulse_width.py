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

for options_file in options_files:
  options = json.load(open(options_file))

  pulse_widths.append(options["flasher"]["width"])
  simulation_times.append(
    (parser.parse(options["finished_at"]) - parser.parse(options["started_at"])).seconds
  )

# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

ax.plot(pulse_widths, simulation_times, "o")

ax.set_xlabel("Flasher pulse width [unit?]")
ax.set_ylabel("Simulation time [s]")
ax.set_title("Flasher simulation performance")

plt.show()
