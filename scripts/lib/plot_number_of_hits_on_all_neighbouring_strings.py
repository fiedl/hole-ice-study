#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/57

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

flasher_data_file = "~/icecube/flasher-data/oux.63_30"
flasher_data = pandas.read_csv(flasher_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"])

simulation_data_file = "~/hole-ice-study/results/flasher_pulse_widths/esca0.05_r0.5rdom_abs100_width127/hits.txt"
simulation_data = pandas.read_csv(simulation_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"], header = 1)

import numpy as np

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

import matplotlib.pyplot as plt
import numpy as np

# prepare canvas
fig, ax = plt.subplots(facecolor="white")

ax.plot(doms, flasher_data_hits, "ro", label = "flasher data 2012")
ax.plot(doms, simulation_data_hits, "bo", label = "simulation")

ax.set_title("Comparing flasher data to simulation, emitting DOM 63_30")
ax.set_xlabel("DOM number ~ z coordinate")
ax.set_ylabel("relative number of hits")

ax.grid()
ax.legend(loc = "upper right")

plt.show()