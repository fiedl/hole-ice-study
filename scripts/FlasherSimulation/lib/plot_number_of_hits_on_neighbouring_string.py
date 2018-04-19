#!/usr/bin/env python

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

# flasher data
flasher_data_file = (sys.argv[1] if (len(sys.argv) > 1) else "~/icecube/flasher-data/oux.62_30")
flasher_data = pandas.read_csv(flasher_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"])
flasher_data = flasher_data[flasher_data.string_number == 63]

# simulation data
simulation_titles = [
  "hole-ice simulation (Run-2018-paYeiy3v, r=0.5 r_dom, esca=5cm)",
  "hole-ice approximation (Run-2018-bi3riu7r)",
  "no hole ice (Run-2018-Fahpon9u)"
]
simulation_data_files = [
  "~/hole-ice-study/scripts/FlasherSimulation/cluster-results/Run-2018-paYeiy3v/hits.txt",
  "~/hole-ice-study/scripts/FlasherSimulation/cluster-results/Run-2018-bi3riu7r/hits.txt",
  "~/hole-ice-study/scripts/FlasherSimulation/cluster-results/Run-2018-Fahpon9u/hits.txt",
]
simulation_plot_styles = ["bo", "go", "yo"]

import matplotlib.pyplot as plt
import numpy as np

# prepare canvas
fig, ax = plt.subplots(facecolor="white")

# normalize
sum_of_all_doms = flasher_data["charge"].sum()

# plot number of hits for each receiving dom
ax.plot(
  sorted(flasher_data["dom_number"].unique()),
  list(flasher_data.groupby(["dom_number"])["charge"].sum() / sum_of_all_doms),
  "ro",
  label = "flasher data 2012"
)

# ax.set_yscale("log")

# extract relevant simulation data
for i, simulation_title in enumerate(simulation_titles):
  simulation_data = pandas.read_csv(simulation_data_files[i], delim_whitespace = True)
  simulation_data = simulation_data[simulation_data.string == 63]

  # normalize
  sum_of_all_doms = simulation_data["charge"].sum()

  ax.plot(
    sorted(simulation_data["dom"].unique()),
    list(simulation_data.groupby(["dom"])["charge"].sum() / sum_of_all_doms),
    simulation_plot_styles[i],
    label = simulation_titles[i]
  )

ax.set_title("Comparing flasher data to simulation, emitting DOM 62_30")
ax.set_xlabel("DOM number on string 63")
ax.set_ylabel("normalized number of hits")

ax.grid()
ax.legend(loc = "upper right")

plt.show()