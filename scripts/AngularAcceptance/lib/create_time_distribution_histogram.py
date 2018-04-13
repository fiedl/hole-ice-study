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
fig, axes = plt.subplots(1, len(data_files), facecolor="white", squeeze=False)

for index, data_file in enumerate(data_files):

  # subplot
  ax = axes[0][index]
  title = data_file.split("/")[-1]

  # read and filter data
  if ".txt" in title: # simulation data
    data = pandas.read_csv(data_file, delim_whitespace=True)
    receiver_data = data[data.string == 63][data.dom == 30]
    title = title + " (simulation)"

    bin_width = 25
    ax.hist(receiver_data["time"], bins = np.arange(min(receiver_data["time"]), max(receiver_data["time"]) + bin_width, bin_width))

  else: # flasher data
    data = pandas.read_csv(data_file, delim_whitespace=True, names = ["string_number", "dom_number", "time", "charge"])
    receiver_data = data[data.string_number == 63][data.dom_number == 30]
    title = title + " (data)"

    ax.hist(receiver_data["time"], len(receiver_data["time"]), weights = receiver_data["charge"])

  ax.set_xlabel("Arrival time after emission [ns]")
  ax.set_ylabel("Collected charge [unit?]")
  ax.set_title(title)

plt.show()
