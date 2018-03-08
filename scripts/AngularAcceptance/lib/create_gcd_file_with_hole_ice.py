#!/usr/bin/env python

from optparse import OptionParser
import glob
from os.path import expandvars

from icecube import dataclasses
from icecube.dataclasses import *
from icecube import icetray, dataio, phys_services, clsim
from icecube.icetray import I3Tray
from icecube import simclasses
from I3Tray import * # otherwise the C++ modules have the wrong signatures


parser = OptionParser(usage = "Usage: python create_gcd_file_with_hole_ice options")
parser.add_option("--input-gcd-file")
parser.add_option("--output-gcd-file")
# parser.add_option("--cylinder-position-and-radius", "--xyr", action="append", help="Format: 'x,y,r'. Allowed multiple times like this: --xyr 200,200,1 --xyr 300,300,1.")
parser.add_option("--cylinder-x", type = "float", action="append")
parser.add_option("--cylinder-y", type = "float", action="append")
parser.add_option("--cylinder-z", type = "float", action="append")
parser.add_option("--cylinder-radius", type = "float", action="append")
(options, args) = parser.parse_args()

hole_ice_cylinders = []
if options.cylinder_x:
  for i, opt in enumerate(options.cylinder_x): # http://stackoverflow.com/a/2756310/2066546
    cylinder = {
      "position": dataclasses.I3Position(options.cylinder_x[i], options.cylinder_y[i], options.cylinder_z[i]),
      "radius": options.cylinder_radius[i]
    }
    hole_ice_cylinders.append(cylinder)

def add_hole_ice_to_geometry_frame(frame, positions = [], radii = []):
    frame.Put("HoleIceCylinderPositions", positions)
    frame.Put("HoleIceCylinderRadii", radii)

def create_hole_ice_gcd_file(input_gcd, output_gcd, hole_ice_cylinders):
    hole_ice_cylinder_positions = dataclasses.I3VectorI3Position()
    hole_ice_cylinder_radii = dataclasses.I3VectorFloat()

    if len(hole_ice_cylinders) > 0:
      hole_ice_cylinder_positions = dataclasses.I3VectorI3Position(
          [cylinder["position"] for cylinder in hole_ice_cylinders]
      )
      hole_ice_cylinder_radii = dataclasses.I3VectorFloat(
          [cylinder["radius"] for cylinder in hole_ice_cylinders]
      )

    tray = I3Tray()
    tray.AddModule("I3Reader",
                   Filename = input_gcd)
    tray.AddModule(add_hole_ice_to_geometry_frame,
                   positions = hole_ice_cylinder_positions,
                   radii = hole_ice_cylinder_radii,
                   Streams = [icetray.I3Frame.Geometry])
    tray.AddModule("I3Writer",
                   Filename = output_gcd)
    tray.AddModule("TrashCan")
    tray.Execute()
    tray.Finish()

create_hole_ice_gcd_file(
  input_gcd = options.input_gcd_file,
  output_gcd = options.output_gcd_file,
  hole_ice_cylinders = hole_ice_cylinders)
