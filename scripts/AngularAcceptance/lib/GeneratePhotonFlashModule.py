#
# Template used: https://github.com/claudiok/clsim/blob/master/python/FakeFlasherInfoGenerator.py
#

from icecube import icetray, dataclasses
from I3Tray import I3Units
from icecube.dataclasses import I3Position
from icecube.dataclasses import *
from icecube.clsim import I3CLSimFlasherPulse, I3CLSimFlasherPulseSeries
from datetime import datetime


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
        self.AddOutBox("OutBox")

    def Configure(self):
        self.series_frame_key = self.GetParameter("SeriesFrameKey")
        self.photon_position = self.GetParameter("PhotonPosition")
        self.photon_direction = self.GetParameter("PhotonDirection")
        self.num_of_photons = self.GetParameter("NumOfPhotons")
        self.pulse_type = self.GetParameter("FlasherPulseType")

    def DAQ(self, frame):
        pulse = I3CLSimFlasherPulse()
        pulse.SetPos(self.photon_position)
        pulse.SetDir(self.photon_direction)
        pulse.SetTime(0.0*I3Units.ns)
        pulse.SetNumberOfPhotonsNoBias(self.num_of_photons)
        pulse.SetType(self.pulse_type)

        # Alexander:
        pulse.SetPulseWidth(1. * I3Units.ns)
        pulse.SetAngularEmissionSigmaPolar( 0.001 * I3Units.deg )
        pulse.SetAngularEmissionSigmaAzimuthal( 0.001 * I3Units.deg )

        pulse_series = I3CLSimFlasherPulseSeries()
        if frame.Has(self.series_frame_key):
          pulse_series = frame.Get(self.series_frame_key)
          frame.Delete(self.series_frame_key)

        pulse_series.append(pulse)

        frame[self.series_frame_key] = pulse_series
        self.PushFrame(frame, "OutBox")
