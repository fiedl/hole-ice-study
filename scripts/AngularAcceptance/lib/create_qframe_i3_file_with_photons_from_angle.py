#!/usr/bin/env python

from icecube.icetray import I3Tray
from I3Tray import * # otherwise the C++ modules have the wrong signatures

from icecube import dataclasses
from icecube.dataclasses import *
from icecube import icetray, dataio, phys_services, clsim

from GeneratePhotonFlashModule import GeneratePhotonFlashModule

import argparse


parser = argparse.ArgumentParser(description="This script creates photons at the given position and stores them in a qframe in an .i3 output file.")
parser.add_argument('--photon-position', type=str, help="e.g. '123,132,145' for 'x,y,z'", required=True)
parser.add_argument('--photon-direction-theta', type=float)
parser.add_argument('--photon-direction-phi', type=float)
parser.add_argument('--photon-direction', type=str)
parser.add_argument('--number-of-photons', type=int, required=True)
parser.add_argument('--gcd-file', type=str, required=True)
parser.add_argument('--output-file', type=str, required=True)
parser.add_argument('--number-of-runs', type=int, default=1)
args = parser.parse_args()

photon_position = I3Position(*[float(coordinate) for coordinate in args.photon_position.split(",")])

if args.photon_direction:
    photon_direction = I3Direction(*[float(coordinate) for coordinate in args.photon_direction.split(",")])
else:
    photon_direction = I3Direction()
    photon_direction.set_theta_phi(args.photon_direction_theta, args.photon_direction_phi)

number_of_photons = args.number_of_photons
number_of_runs = args.number_of_runs
gcd_file = args.gcd_file
output_file = args.output_file

number_of_frames = number_of_runs
if gcd_file:
    number_of_frames += 4 # info, geometry, calibration, detector

print "photon_position="
print photon_position
print "photon_direction="
print photon_direction
print "number_of_photons="
print number_of_photons
print "output_file="
print output_file


tray = I3Tray()
tray.AddModule("I3InfiniteSource",
               Prefix = gcd_file,
               Stream = icetray.I3Frame.DAQ)
tray.AddModule(GeneratePhotonFlashModule,
               SeriesFrameKey = "PhotonFlasherPulseSeries",
               PhotonPosition = photon_position,
               PhotonDirection = photon_direction,
               NumOfPhotons = number_of_photons, # 1.7e5,
               FlasherPulseType = clsim.I3CLSimFlasherPulse.FlasherPulseType.LED340nm)
tray.AddModule("I3Writer",
               Filename = output_file)
tray.AddModule("TrashCan")
tray.Execute(number_of_frames)
tray.Finish()

