#!/usr/bin/env python

from optparse import OptionParser
from os.path import expandvars

parser = OptionParser()
parser.add_option("--gcd",
  default = expandvars("$I3_TESTDATA/sim/GeoCalibDetectorStatus_IC86.55380_corrected.i3.gz"))
parser.add_option("--string", type = "int", default = 62)
parser.add_option("--dom", type = "int", default = 30)
parser.add_option("--seed", type = "int", default = 12344)
parser.add_option("--number-of-events", type = "int", default = 1)
parser.add_option("--brightness", type = "int", default = 40)
parser.add_option("--width", type = "int", default = 20)
parser.add_option("--mask", type = "int", default = 0b0001)
parser.add_option("--outfile", default = "simulated_flashes.i3")

(options, args) = parser.parse_args()

from I3Tray import *
from icecube import icetray, dataclasses, dataio, phys_services, clsim, sim_services

tray = I3Tray()

randomService = phys_services.I3SPRNGRandomService(
  seed = options.seed,
  nstreams = 10000,
  streamnum = 1)

tray.AddModule("I3InfiniteSource", "streams",
  Prefix = options.gcd,
  Stream = icetray.I3Frame.DAQ)

tray.AddModule("I3MCEventHeaderGenerator", "gen_header",
  Year = 2012,
  DAQTime = 7968509615844458,
  RunNumber = 1,
  EventID = 1,
  IncrementEventID = True)

tray.AddModule(clsim.FakeFlasherInfoGenerator, "FakeFlasherInfoGenerator",
  FlashingDOM = icetray.OMKey(options.string, options.dom),
  FlasherTime = 0.*I3Units.ns,
  #FlasherMask = 0b111111000000, # only the 6 horizontal LEDs,  0-5 are tilted, 6-11 are horizontal [cDOM LEDs are all horizantal]
  #FlasherMask = 0b10101, # 505nm LEDs only (on a cDOM)
  #FlasherBrightness = 127, # full brightness
  #FlasherWidth = 127)      # full width
  FlasherMask = options.mask,
  FlasherBrightness = options.brightness,
  FlasherWidth = options.width)

tray.AddModule("I3Writer", "writer",
  Filename = options.outfile)

tray.AddModule("TrashCan", "the can")

tray.Execute(options.number_of_events + 4)
tray.Finish()
