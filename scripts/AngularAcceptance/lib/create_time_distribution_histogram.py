import sys
import pandas

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

data_files = sys.argv[1:]

# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

weights_array = []
bins_array = []
titles_array = []

time_min = 500
time_max = 3000 # ns

for index, data_file in enumerate(data_files):
  title = ""

  # flasher data files are already binned (width = 25ns).
  if ".txt" in data_file: # simulation data
    data = pandas.read_csv(data_file, delim_whitespace=True)
    receiver_data = data[data.string == 63][data.dom == 30]
    receiver_data = receiver_data[receiver_data.time < time_max][receiver_data.time > time_min] # cut
    title = data_file.split("/")[-2] + " (simulation)"

    # simulation data needs to be binned.
    bin_width = 25
    bins = range(time_min, time_max, bin_width)
    weights, time_edges = np.histogram(receiver_data["time"], bins + [max(bins) + bin_width])

  else: # flasher data
    data = pandas.read_csv(data_file, delim_whitespace=True, names = ["string_number", "dom_number", "time", "charge"])
    receiver_data = data[data.string_number == 63][data.dom_number == 30]
    receiver_data = receiver_data[receiver_data.time < time_max][receiver_data.time > time_min] # cut
    title = data_file.split("/")[-1] + " (data)"

    bins = receiver_data["time"]
    weights = receiver_data["charge"]

  bins_array.append(bins)
  weights_array.append(weights)
  titles_array.append(title)

ax.hist(bins_array, (time_max - time_min)/25/3, weights = weights_array, label = titles_array, normed = True)

ax.set_xlabel("Arrival time after emission [ns]")
ax.set_ylabel("Collected charge [unit?]")

plt.legend(loc='upper right')
plt.show()
