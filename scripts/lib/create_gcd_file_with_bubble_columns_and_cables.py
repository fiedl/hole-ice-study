#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/61

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

# Data source
string_positions_file = "~/icecube/string_positions.txt"
dom_positions_file = "~/icecube/dom_positions.txt"
cable_positions_file = "~/icecube/cable-data/icecube.wisc.edu/~dima/work/IceCube-ftp/leds/results.txt"

string_positions_headers = ["x", "y"]
dom_positions_headers = ["string", "dom", "x", "y", "z"]
cable_positions_headers = ["string", "dom", "tilt_nx", "tilt_ny", "tilt_nz", "tilt_error", "cable_dir", "cable_error", "led7_dir", "led_best_bin_dir", "led_parabola_dir", "led_parabola_error", "led_sin_dir", "led_sin_error", "led_weight_sin_dir", "led_weight_sind_error"]

input_gcd_file = "$I3_TESTDATA/sim/GeoCalibDetectorStatus_IC86.55380_corrected.i3.gz"

# Data destination
destination_gcd_file = "~/icecube/gcd_with_bubble_columns_and_cables.i3"

# Material properties
bubble_column_effective_scattering_length = 0.05 # metres
bubble_column_absorption_length = 100.0 # metres
bubble_column_radius_in_dom_radii = 0.5

cable_effective_scattering_length = 100.0 # metres
cable_absorption_length = 0.0
cable_radius = 0.02 # metres

dom_radius = 0.16510 # metres


from optparse import OptionParser
import glob

import os
from os.path import expandvars
import sys
import pandas
import numpy as np

# Command line interface
parser = OptionParser(usage = "Usage: python create_gcd_file_with_bubble_columns_and_cables.py options")
parser.add_option("--esca", type = "float", help = "Effective scattering length of the bubble columns in metres")
parser.add_option("--radius-in-dom-radii", type = "float", help = "Radius of the bubble columns in DOM radii")
(options, args) = parser.parse_args()

bubble_column_effective_scattering_length = options.esca if options.esca else bubble_column_effective_scattering_length
bubble_column_radius_in_dom_radii = options.radius_in_dom_radii if options.radius_in_dom_radii else bubble_column_radius_in_dom_radii

def expand_path(filename):
  return os.path.expandvars(os.path.expanduser(filename))

def read_csv(filename, headers):
  return pandas.read_csv(expand_path(filename), delim_whitespace = True, names = headers)

string_positions = read_csv(string_positions_file, string_positions_headers)
dom_positions = read_csv(dom_positions_file, dom_positions_headers)
cable_positions = read_csv(cable_positions_file, cable_positions_headers)

def first(array):
  return array.iloc[0]

def dom_x(string, dom):
  global dom_positions
  return first(dom_positions[dom_positions.string == string][dom_positions.dom == dom]["x"])

def dom_y(string, dom):
  global dom_positions
  return first(dom_positions[dom_positions.string == string][dom_positions.dom == dom]["y"])

def dom_z(string, dom):
  global dom_positions
  return first(dom_positions[dom_positions.string == string][dom_positions.dom == dom]["z"])

def string_x(string):
  global string_positions
  return string_positions["x"][string - 1]

def string_y(string):
  global string_positions
  return string_positions["y"][string - 1]

def has_cable_position(string, dom):
  return True if len(cable_positions[cable_positions.string == string][cable_positions.dom == dom]) > 0 else False

def cable_angle_from_grid_north_in_degrees(string, dom):
  return first(cable_positions[cable_positions.string == string][cable_positions.dom == dom]["cable_dir"])

def cable_angle_from_grid_north_in_rad(string, dom):
  return cable_angle_from_grid_north_in_degrees(string, dom) * 2.0 * np.pi / 360

def cable_x(string, dom):
  global dom_radius, cable_radius
  return dom_x(string, dom) + np.sin(cable_angle_from_grid_north_in_rad(string, dom)) * (dom_radius + cable_radius)

def cable_y(string, dom):
  global dom_radius, cable_radius
  return dom_y(string, dom) + np.cos(cable_angle_from_grid_north_in_rad(string, dom)) * (dom_radius + cable_radius)

def cable_z(string, dom):
  return dom_z(string, dom)


# Compose cylinders
cylinder_positions = []
cylinder_radii = []
cylinder_scattering_lengths = []
cylinder_absorption_lengths = []

for string in range(1, 78):
  cylinder_positions.append([string_x(string), string_y(string), 0])
  cylinder_radii.append(bubble_column_radius_in_dom_radii * dom_radius)
  cylinder_scattering_lengths.append(bubble_column_effective_scattering_length * (1 - 0.94))
  cylinder_absorption_lengths.append(bubble_column_absorption_length)

for string in range(1, 78):
  for dom in range(1, 60):
    if has_cable_position(string, dom):
      cylinder_positions.append([cable_x(string, dom), cable_y(string, dom), cable_z(string, dom)])
      cylinder_radii.append(cable_radius)
      cylinder_scattering_lengths.append(cable_effective_scattering_length * (1 - 0.94))
      cylinder_absorption_lengths.append(cable_absorption_length)

# Process i3 file
from icecube import dataclasses
from icecube.dataclasses import *
from icecube import icetray, dataio, phys_services, clsim
from icecube.icetray import I3Tray
from icecube import simclasses
from I3Tray import * # otherwise the C++ modules have the wrong signatures

def add_hole_ice_to_geometry_frame(frame, positions = [], radii = [], scattering_lengths = [], absorption_lengths = []):
  positions = (dataclasses.I3Position(pos[0], pos[1], pos[2]) for pos in positions)
  frame.Put("HoleIceCylinderPositions", dataclasses.I3VectorI3Position(positions))
  frame.Put("HoleIceCylinderRadii", dataclasses.I3VectorFloat(radii))
  frame.Put("HoleIceCylinderScatteringLengths", dataclasses.I3VectorFloat(scattering_lengths))
  frame.Put("HoleIceCylinderAbsorptionLengths", dataclasses.I3VectorFloat(absorption_lengths))

tray = I3Tray()
tray.AddModule("I3Reader",
               Filename = expand_path(input_gcd_file))
tray.AddModule(add_hole_ice_to_geometry_frame,
               positions = cylinder_positions,
               radii = cylinder_radii,
               scattering_lengths = cylinder_scattering_lengths,
               absorption_lengths = cylinder_absorption_lengths,
               Streams = [icetray.I3Frame.Geometry])
tray.AddModule("I3Writer",
               Filename = expand_path(destination_gcd_file))
tray.AddModule("TrashCan")
tray.Execute()
tray.Finish()

print "Output file: " + destination_gcd_file
