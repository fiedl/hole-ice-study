#!/usr/bin/env python

from optparse import OptionParser
from os.path import expandvars

parser = OptionParser()
parser.add_option("--i3-file")
parser.add_option("--outfile", default = "tmp/read_out_hits.txt")

(options, args) = parser.parse_args()

input_file = options.i3_file

from I3Tray import *
from icecube import icetray, dataclasses, dataio, phys_services, clsim, sim_services

# <I3FrameObject class_name="I3MCPESeriesMap" version="0">
#   <map version="0">
#     <count>7</count>
#     <item version="0">
#       <first version="2">
#         <StringNumber>62</StringNumber>
#         <OMNumber>25</OMNumber>
#         <PMTNumber>0</PMTNumber>
#       </first>
#       <second version="0">
#         <count>1</count>
#         <item version="1">
#           <time>451.3367919921875</time>
#           <npe>1</npe>
#           <major_ID>0</major_ID>
#           <minor_ID>0</minor_ID>
#         </item>
#       </second>
#     </item>

# hits = [0] * 59
# def read_out_hits(frame):
#   for index, dom_number in enumerate(range(1, 60)):
#     om_key = OMKey(options.string, dom_number)
#     n = 0
#     if not frame['MCPESeriesMap'].get(om_key) is None:
#       n = len(frame['MCPESeriesMap'].get(om_key))
#     hits[index] = n

import pandas

data = pandas.DataFrame([])
def read_out_hits(frame):
  global data
  for dom_key, photons in frame['MCPESeriesMap'].iteritems():
    for photon in photons:
      data = data.append(pandas.DataFrame({
        "string": key.string,
        "dom": key.om,
        "time": photon.time,
        "charge": photon.npe
      }, index = [0]), ignore_index = True)

tray = I3Tray()

tray.AddModule("I3Reader", "reader",
  Filename = input_file)

tray.AddModule(read_out_hits,
  Streams = [icetray.I3Frame.DAQ])

tray.Execute()
tray.Finish()

#print("HITS = " + str(hits))

data.to_csv(options.outfile, sep=" ", header = True, index = False,
    columns = ["string", "dom", "time", "hits"])

