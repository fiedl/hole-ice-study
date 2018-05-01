#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/57

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

flasher_data_file = "~/icecube/flasher-data/oux.63_30"
flasher_data = pandas.read_csv(flasher_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"])

import os
import glob2

simulation_data_files = []
if len(sys.argv) > 1:
  base_path = sys.argv[1]
  simulation_data_files = list(glob2.glob(os.path.join(os.path.expanduser(base_path), "./**/hits.txt")))
if len(simulation_data_files) == 0:
  simulation_data_files.append("~/hole-ice-study/results/flasher_pulse_widths/esca0.05_r0.5rdom_abs100_width127/hits.txt")

import numpy as np
import matplotlib.pyplot as plt

for simulation_data_file in simulation_data_files:
  simulation_data = pandas.read_csv(simulation_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"], header = 1)

  # for all receiving strings, which are located around the
  # sending string 63, collect the photon hits for each
  # dom.
  #
  receiving_strings = [62, 54, 55, 64, 71, 70]
  doms = range(1, 60)
  def extract_hits(data):
    global receiving_strings
    global doms
    number_of_total_hits_in_detector = data["charge"].sum()
    number_of_total_hits_in_receiving_strings = data[data.string_number.isin(receiving_strings)]["charge"].sum()
    hits = []
    for dom in doms:
      hits_at_this_z = data \
        [data.string_number.isin(receiving_strings)] \
        [data.dom_number == dom] \
        ["charge"].sum()
      hits.append(hits_at_this_z)
    relative_hits = np.asarray(hits) * 1.0 / number_of_total_hits_in_detector
    return relative_hits
  flasher_data_hits = extract_hits(flasher_data)
  simulation_data_hits = extract_hits(simulation_data)

  # prepare canvas
  fig, ax = plt.subplots(facecolor="white")

  ax.plot(doms, flasher_data_hits, "ro", label = "flasher data 2012, total hits = " + str(flasher_data["charge"].sum()))
  ax.plot(doms, simulation_data_hits, "bo", label = "simulation, total hits = " + str(simulation_data["charge"].sum()))

  ax.set_title("Comparing flasher data to simulation, emitting DOM 63_30")
  ax.set_xlabel("DOM number ~ z coordinate")
  ax.set_ylabel("number of hits / total number of hits in whole detector")

  ax.grid()
  ax.legend(loc = "upper right")

  plt.show()