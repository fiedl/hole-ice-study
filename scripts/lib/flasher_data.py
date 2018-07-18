#!/usr/bin/env python

# Usage
#
#     import flasher_data
#
#     data = flasher_data.all()
#     data = data[data.string_number == 60]["charge"].sum()

import pandas

def source_file():
  return "~/icecube/flasher-data/oux.63_30"

def all():
  return pandas.read_csv(source_file(), delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"])

def brightness():
  return 127

def width():
  return 127

def scaling():
  return 1.0 * brightness() * width()

