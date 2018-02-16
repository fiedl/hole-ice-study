# steamshovel/python/artists/HoleIce.py

from icecube.shovelart import *
from icecube.dataclasses import I3Constants
from icecube import dataclasses

class HoleIce(PyArtist):

    numRequiredKeys = 0
    requiredTypes = [ dataclasses.I3VectorI3Position, dataclasses.I3VectorFloat ]

    def __init__(self):
        PyArtist.__init__(self)
        # self.defineSettings( { "Show ice": True, "Show bedrock": True, "Linewidth":RangeSetting(.1,10.,1000,100) } )

    def description( self ):
        return "Hole Ice Cylinder"

    # @param PyArtist self
    # @param I3Frame frame
    # @param SceneGroup output
    #
    def create( self, frame, output ):

        hole_ice_cylinder_positions = frame[list(self.keys())[0]]
        hole_ice_cylinder_radii = frame[list(self.keys())[1]]

        bedrock_z = -I3Constants.OriginElev
        ice_top_z = I3Constants.zIceTop

        for i, position in enumerate(hole_ice_cylinder_positions):
            radius = hole_ice_cylinder_radii[i]

            # If z is given, draw a cylinder of 1m height.
            # If z is 0, draw a cylinder from the very top to the very bottom.
            #
            # See: https://github.com/fiedl/hole-ice-study/issues/34
            #
            if position.z == 0:

              position_vec = vec3d(position.x, position.y, bedrock_z)
              cylinder = output.addCylinder(
                  position_vec,                           # Vertex
                  vec3d(0, 0, ice_top_z - bedrock_z),     # Axes
                  radius,                                 # Base Radius
                  radius                                  # Top Radius
              )
              cylinder.setColor(PyQColor(255, 255, 255, 120))

            else:

              position_vec = vec3d(position.x, position.y, position.z - 0.5)
              cylinder = output.addCylinder(
                  position_vec,                           # Vertex
                  vec3d(0, 0, 1.0),                       # Axes
                  radius,                                 # Base Radius
                  radius                                  # Top Radius
              )
              cylinder.setColor(PyQColor(255, 255, 255, 120))
