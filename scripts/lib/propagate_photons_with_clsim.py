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


### Command line options
# =============================================================================

parser = OptionParser(usage = "Usage: python propagate_photons_with_clsim.py options infile1.i3 infile2.i3 ...")
parser.add_option("--scattering-factor", "--sca", type = "float", default = 1.0)
parser.add_option("--absorption-factor", "--abs", type = "float", default = 1.0)
parser.add_option("--output-i3-file", help = "I3 File to write the numbers of dom hits for each run to, e.g. tmp/numbers_of_dom_hits.i3")
parser.add_option("--output-text-file", help = "File to write the number of dom hits for each run to, one line per run, e.g. tmp/numbers_of_dom_hits.txt", default = "tmp/number_of_dom_1_1_hits.txt")
parser.add_option("--ice-model", dest = "ice_model_file", help = "e.g. $I3_SRC/clsim/resources/ice/spice_mie")
parser.add_option("--seed", type = "int", help = "e.g. 123456")
parser.add_option("--save-photon-paths", help = "True or False")
parser.add_option("--use-gpus", help = "True or False")
parser.add_option("--number-of-parallel-runs", type = "int")
parser.add_option("--number-of-frames", type = "int", default = 0)
parser.add_option("--use-hole-ice-approximation", help = "Use angular acceptance modification (UseHoleIceParameterization), but no simulated hole ice.")
parser.add_option("--use-hole-ice-simulation", help = "Simulate hole ice in the propagation kernel with the --scattering-factor and the --absorption-factor parameters.")
parser.add_option("--use-flasher-info-vect", default = False)

(options, args) = parser.parse_args()

input_files = args

if isinstance(input_files, basestring):
    input_files = eval(input_files)

if isinstance(options.use_gpus, basestring):
    options.use_gpus = eval(options.use_gpus)

if isinstance(options.save_photon_paths, basestring):
    options.save_photon_paths = eval(options.save_photon_paths)

if isinstance(options.use_hole_ice_approximation, basestring):
    options.use_hole_ice_approximation = eval(options.use_hole_ice_approximation)

if isinstance(options.use_hole_ice_simulation, basestring):
    options.use_hole_ice_simulation = eval(options.use_hole_ice_simulation)

# if options.infiles == []:
#     options.infiles = ["angular_scan_gcd_with_hole_ice.i3"] + options.number_of_runs * glob.glob("angular_scan_qframes/*.i3")

# Further options, manually set here:
om_key = OMKey(1,1)


### Photon Propagation with clsim
# =============================================================================

counter = 0
numbers_of_dom_hits = []
def ReadOutAngularAcceptance(frame):
    global numbers_of_dom_hits
    n = 0
    if (frame['MCPESeriesMap'].items() != []):
        if not frame['MCPESeriesMap'].get(om_key) is None:
            n = len(frame['MCPESeriesMap'].get(om_key))
    numbers_of_dom_hits.append(n)
    global counter
    counter += 1


def PerformPropagationSimulation():
    tray = I3Tray()
    tray.AddModule("I3Reader",
                   FilenameList = input_files)
    tray.AddService("I3SPRNGRandomServiceFactory",
                    Seed = options.seed,
                    NStreams = 2,
                    StreamNum = 1)
    randomService = phys_services.I3SPRNGRandomService(seed = options.seed,
                                                       nstreams = 10000,
                                                       streamnum = 1)


    common_clsim_parameters = dict(
        PhotonSeriesName = "PropagatedPhotons",
        RandomService = randomService,
        UseGPUs = options.use_gpus,
        UseCPUs = not options.use_gpus,
        ParallelEvents = options.number_of_parallel_runs,
        IceModelLocation = options.ice_model_file,
        UnWeightedPhotons = True,
        #UnWeightedPhotonsScalingFactor=0.01,
        DOMOversizeFactor = 1.0,
        UnshadowedFraction = 1.0,
        FlasherInfoVectName = ("I3FlasherInfo" if options.use_flasher_info_vect else ""),
        FlasherPulseSeriesName = ("PhotonFlasherPulseSeries" if not options.use_flasher_info_vect else ""),
        UseHoleIceParameterization = options.use_hole_ice_approximation,  # Angular Acceptance Modification.
    )

    # In production, we do not need to save the photons. Thus, we skip this for
    # performance and disk space reasons. But one can activate
    # `--save-photon-paths` for visualization or debug reasons.
    #
    if options.save_photon_paths:
        tray.AddSegment(clsim.I3CLSimMakePhotons,

                        StopDetectedPhotons = False,
                        PhotonHistoryEntries = 10000,
                        ExtraArgumentsToI3CLSimModule = dict(
                            SaveAllPhotons = True,
                            SaveAllPhotonsPrescale = 1.0,
                            MaxNumOutputPhotonsCorrectionFactor = 1.0,
                            SimulateHoleIce = options.use_hole_ice_simulation,
                            HoleIceScatteringLengthFactor = options.scattering_factor,
                            HoleIceAbsorptionLengthFactor = options.absorption_factor
                        ),

                        **common_clsim_parameters
                        )
        icetray.set_log_level(icetray.I3LogLevel.LOG_DEBUG)
    else:

        extra_args = dict()
        if options.use_hole_ice_simulation:
            extra_args = dict(
                SimulateHoleIce = options.use_hole_ice_simulation,
                HoleIceScatteringLengthFactor = options.scattering_factor,
                HoleIceAbsorptionLengthFactor = options.absorption_factor
                )

        tray.AddSegment(clsim.I3CLSimMakeHits,
                        StopDetectedPhotons = True,
                        ExtraArgumentsToI3CLSimModule = extra_args,
                        **common_clsim_parameters
                        )

    if not options.save_photon_paths:
        # This does only work with the `I3CLSimMakeHits` module, thus does
        # not work with `save_photon_paths`.
        tray.AddModule(ReadOutAngularAcceptance,
                       Streams = [icetray.I3Frame.DAQ])

    tray.AddModule("I3Writer",
                   Filename = options.output_i3_file)
    tray.AddModule("TrashCan")

    if options.number_of_frames == 0:
        tray.Execute()
    else:
        tray.Execute(options.number_of_frames)

    tray.Finish()


### Perform simulation
# =============================================================================

#additional_args = dict(
#   ExtraArgumentsToI3CLSimModule = dict(
#       **save_photon_paths_args
#        #SinglePhotonOptimizations = 2.2e-3,
#        #SimulateHoleIce = True,
#        #HoleIceScatteringLengthFactor = options.scattering_factor,
#        #HoleIceAbsorptionLengthFactor = options.absorption_factor
#    ))

PerformPropagationSimulation()

print "SIMULATION RESULT"
print numbers_of_dom_hits

outfile = open(options.output_text_file, 'w')
for number_of_dom_hits in numbers_of_dom_hits:
  print >> outfile, number_of_dom_hits
outfile.close()
