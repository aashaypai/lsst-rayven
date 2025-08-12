import batoid
import numpy as np

from dataclasses import dataclass, field

@dataclass
class TMA:
    az: float
    alt: float
    band: str
    
    @property
    def model(self):
        return self.get_model()
    
    def _validate_band(self):

        if self.band in ['u', 'g', 'r', 'i', 'z', 'y']:
            return f'LSST_{self.band}.yaml'

        if self.band is None:
            return '../data/CBP/LSST.yaml'
        
        else:
            raise ValueError(f"Band must be either 'u', 'g', 'r', 'i', 'z', 'y' or None, currently: {self.band}")
    
    def get_model(self):

        yaml_path = self._validate_band()
        lsst = batoid.Optic.fromYaml(yaml_path)
        
        elevBearingHeight = 5.425
        m1VertexHeight = 3.53
        rotTelPos = 270
        telAzimuthOffset = 0
        
        # change height
        lsst = lsst.withGlobalShift([0, 0, m1VertexHeight])
        lsst = lsst.withLocallyRotatedOptic("LSSTCamera", batoid.RotZ(np.deg2rad(rotTelPos)))
        
        # rotate to azimuth
        lsst = lsst.withLocalRotation(batoid.RotZ(np.deg2rad(-self.az))) # 90 deg offset from x axis
        
        # rotate to altitude
        lsst = lsst.withLocalRotation(batoid.RotX(np.deg2rad(-(90-self.alt))),
                                      rotCenter=[0, 0, elevBearingHeight], 
            coordSys=batoid.globalCoordSys)

        return lsst

@dataclass
class CBP:
    dome_az: float
    az: float
    alt: float

    @property
    def model(self):
        return self.get_model()

    def polar2cartesian(self, radius, angle_deg):
        x = radius * np.cos(np.deg2rad(angle_deg))
        y = radius * np.sin(np.deg2rad(angle_deg))
        return x, y
    
    def get_model(self):
        cbp = batoid.Optic.fromYaml('CBP.yaml')
        # starting position: Alt = 90 (toward horizon), Az = 0 (facing TMA)
        
        # rotate to CBP azimuth = 0 when the CBP points to the TMA
        cbp = cbp.withLocalRotation(batoid.RotZ(np.deg2rad(-120)))
        
        # calculate CBP x, y, z position
        # 60 degrees CCW from North when Dome slit faces North; Dome rotates CW to a given azimuth
        # 90 deg as x axis is offset from North by that amount
        cbp_x, cbp_y = self.polar2cartesian(12.4, 60+90) # + 90 from x axis
        cbp_z = 12.135 + 0.998  # Height above azimuth ring + height of CBP itself
        
        cbp = cbp.withGlobalShift(
                [cbp_x, 
                 cbp_y, 
                 cbp_z  
                ]
            )
        
        # rotate from pointing to sky (extra -90) to CBP altitude
        cbp = cbp.withLocalRotation(batoid.RotX(np.deg2rad(-90+self.alt)))

        # rotate the Dome
        rot_matrix = [[np.cos(np.deg2rad(-self.dome_az)), -np.sin(np.deg2rad(-self.dome_az)), 0],
                      [np.sin(np.deg2rad(-self.dome_az)), np.cos(np.deg2rad(-self.dome_az)), 0],
                      [0, 0, 1]]
        cbp = cbp.withGlobalRotation(rot=rot_matrix, 
                                     rotCenter=[0, 0, 0],
                                     coordSys=batoid.globalCoordSys)
        
        # rotate to azimuth
        cbp = cbp.withGlobalRotation(batoid.RotZ(np.deg2rad(-self.az)))
        cbp = cbp.withLocallyRotatedOptic("Cassegrain", batoid.RotZ(np.deg2rad(46.5)))

        return cbp