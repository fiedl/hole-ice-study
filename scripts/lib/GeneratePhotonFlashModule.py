#
# Template used: https://github.com/claudiok/clsim/blob/master/python/FakeFlasherInfoGenerator.py
#

from icecube import icetray, dataclasses
from I3Tray import I3Units
from icecube.dataclasses import I3Position
from icecube.dataclasses import *
from icecube.clsim import I3CLSimFlasherPulse, I3CLSimFlasherPulseSeries
from datetime import datetime

import math
import random

class GeneratePhotonFlashModule(icetray.I3Module):
    """
    Generate a Photon Flash into a DAQ Frame.
    """
    def __init__(self, context):
        icetray.I3Module.__init__(self, context)
        self.AddParameter("SeriesFrameKey",
                          "Name of the I3Frame Key the photon flash should be written to",
                          "PhotonFlasherPulseSeries")
        self.AddParameter("PhotonPosition",
                          "The position of the photon source.",
                          I3Position(0,0,0))
        self.AddParameter("PhotonDirection",
                          "The direction of the photon source",
                          I3Direction(0,0,0))
        self.AddParameter("NumOfPhotons",
                          "The number of photons to inject from the given position.",
                          1)
        self.AddParameter("FlasherPulseType",
                          "The I3CLSimFlasherPulse.FlasherPulseType of the photon flashs. For a list, see: https://github.com/claudiok/clsim/blob/master/public/clsim/I3CLSimFlasherPulse.h#L59",
                          I3CLSimFlasherPulse.FlasherPulseType.LED340nm)
        self.AddParameter("PlaneWave",
                          "Whether to start the photons from a plane rather than a point",
                          False)
        self.AddParameter("PlaneWaveSize",
                          "How big should the plane be in metres, e.g. 1.0.",
                          1.0)
        self.AddParameter("Seed",
                          "Seed for the random number generator",
                          1234)
        self.AddOutBox("OutBox")

    def Configure(self):
        self.series_frame_key = self.GetParameter("SeriesFrameKey")
        self.photon_position = self.GetParameter("PhotonPosition")
        self.photon_direction = self.GetParameter("PhotonDirection")
        self.num_of_photons = self.GetParameter("NumOfPhotons")
        self.pulse_type = self.GetParameter("FlasherPulseType")
        self.plane_wave = self.GetParameter("PlaneWave")
        self.plane_wave_size = self.GetParameter("PlaneWaveSize")
        self.seed = self.GetParameter("Seed")

    def generate_pulse(self, photon_position, photon_direction, number_of_photons):
      pulse = I3CLSimFlasherPulse()
      pulse.SetPos(photon_position)
      pulse.SetDir(photon_direction)
      pulse.SetTime(0.0*I3Units.ns)
      pulse.SetNumberOfPhotonsNoBias(number_of_photons)
      pulse.SetType(self.pulse_type)

      # Alexander:
      pulse.SetPulseWidth(1. * I3Units.ns)
      pulse.SetAngularEmissionSigmaPolar( 0.001 * I3Units.deg )
      pulse.SetAngularEmissionSigmaAzimuthal( 0.001 * I3Units.deg )

      return pulse

    def DAQ(self, frame):
        random.seed(self.seed)

        pulse_series = I3CLSimFlasherPulseSeries()

        if self.plane_wave:
          for i in xrange(self.num_of_photons):
            random_vector = I3Position(random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1)
            shift_vector_a = self.photon_direction.cross(random_vector)
            shift_vector_b = self.photon_direction.cross(shift_vector_a)
            len_a = math.sqrt(shift_vector_a * shift_vector_a)
            len_b = math.sqrt(shift_vector_b * shift_vector_b)
            new_photon_position = self.photon_position + \
                shift_vector_a / len_a * (random.random() * 2 - 1) * self.plane_wave_size / 2 + \
                shift_vector_b / len_b * (random.random() * 2 - 1) * self.plane_wave_size / 2
            pulse = self.generate_pulse(new_photon_position, self.photon_direction, 1)
            pulse_series.append(pulse)
        else:
          pulse = self.generate_pulse(self.photon_position, self.photon_direction, self.num_of_photons)
          pulse_series.append(pulse)

        frame[self.series_frame_key] = pulse_series
        self.PushFrame(frame, "OutBox")
