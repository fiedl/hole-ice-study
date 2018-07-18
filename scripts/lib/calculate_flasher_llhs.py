#!/usr/bin/env python

# Calculate log likelihood (LLH) for flasher data vs. simulation.
# https://github.com/fiedl/hole-ice-study/issues/95

# Usage: ./calculate_flasher_llhs.py ~/hole-ice-study/results/flasher_parameter_scan_full_brightness_with_thinning

# This will calculate the LLH for each run within the given data directory
# and append the "llh" to the "options.json" files within.


import cli
import options
import flasher_llh

print "Calculating flasher LLHs"

for data_dir in cli.data_dirs():
  print "  " + data_dir

  llh = flasher_llh.calculate(data_dir)
  print "    LLH = " + str(llh)

  options.append(data_dir, {"llh": llh})