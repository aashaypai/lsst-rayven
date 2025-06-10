from dataclasses import dataclass

from lsst.obs.lsst import LsstCam

@dataclass(frozen=True)
class LSSTCamConstants:
    telescope_components: tuple = ('L1_entrance', 'L1_exit', 'L2_entrance', 'L2_exit', 'Filter_entrance', 'Filter_exit', 'L3_entrance', 'L3_exit', 'Detector')

    telescope_component_labels: tuple = ('L11', 'L12', 'L21', 'L22', 'F1', 'F2',
                                         'L31', 'L32', 'D')
                                         
    bands: tuple = ('u', 'g', 'r', 'i', 'z', 'y')

    median_wavelengths = dict(u=372, g=481, r=622, i=756, z=868, y=975) ##nm
    
    pixel_to_arcsec: float = 0.2  # arcsec/pixel

    focal_plane_bbox = LsstCam.getCamera().getFpBBox()
    fp_min_x, fp_max_x = focal_plane_bbox.getMinX(), focal_plane_bbox.getMaxX()
    fp_min_y, fp_max_y = focal_plane_bbox.getMinY(), focal_plane_bbox.getMaxY()
    fp_width, fp_height = focal_plane_bbox.getWidth(), focal_plane_bbox.getHeight()
