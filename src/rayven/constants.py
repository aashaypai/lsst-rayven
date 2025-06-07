from dataclasses import dataclass

@dataclass(frozen=True)
class LSSTCamConstants:
    telescope_components: tuple = ('L1_entrance', 'L1_exit', 'L2_entrance', 'L2_exit', 'Filter_entrance', 'Filter_exit', 'L3_entrance', 'L3_exit', 'Detector')
    
    filters: tuple = ('u', 'g', 'r', 'i', 'z', 'y')

    median_wavelengths = dict(u=372, g=481, r=622, i=756, z=868, y=975) ##nm
    
    pixel_to_arcsec: float = 0.2  # arcsec/pixel
