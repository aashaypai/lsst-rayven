from .constants import LSSTCamConstants

import batoid
import numpy as np
from astropy.table import QTable

class BatoidSimulator:

    def __init__(self, obs_params, reflectance, star_table, scaling, verbose):

        self._verbose = verbose
        
        self.obs_params = obs_params
        self.telescope = batoid.Optic.fromYaml(f"LSST_{self.obs_params.band}.yaml")
        
        self.reflectance = reflectance
        
        self._validate_star_table(star_table)
        self.star_table = star_table
        self.num_stars = len(star_table)
        
        self.scaling = self.set_scaling(scaling)
        

    def _validate_star_table(self, table):
        if not isinstance(table, QTable):
            raise TypeError(f"star table must be an astropy.table.QTable object")
            
        required_cols = {'ra', 'dec', 'mag', 'flux', 'fa_x', 'fa_y'}
        if not required_cols.issubset(table.colnames):
            missing = required_cols - set(table.colnames)
            raise ValueError(f"camera geometry coordinate transform table is missing required column(s): {', '.join(missing)}")

    def set_scaling(self, scaling):

        match scaling:
            case 'constant':
                return [1]*self.num_stars
            case 'flux':
                return self.star_table['flux'].value
            case 'mag':
                return self.star_table['mag'].value
            case _:
                raise ValueError(f"Batoid scaling must be 'flux', 'mag' or 'constant', currently: {scaling}")

    def set_optic_reflectance(self):

        for surface in self.telescope.itemDict.values():

            # L1, L2, L3 reflectances
            if surface.name in self.reflectance.values.keys()and isinstance(surface, batoid.RefractiveInterface):
                surface.forwardCoating = batoid.SimpleCoating(self.reflectance.values[surface.name], 
                                                              1-self.reflectance.values[surface.name])
                
                surface.reverseCoating = batoid.SimpleCoating(self.reflectance.values[surface.name], 
                                                              1-self.reflectance.values[surface.name])
            # Filter reflectances
            elif 'Filter' in surface.name and isinstance(surface, batoid.RefractiveInterface):
                surface.forwardCoating = batoid.SimpleCoating(
                    self.reflectance.values[f'{self.obs_params.band}{surface.name[6:]}'], 
                    1-self.reflectance.values[f'{self.obs_params.band}{surface.name[6:]}'])
                
                surface.reverseCoating = batoid.SimpleCoating(
                    self.reflectance.values[f'{self.obs_params.band}{surface.name[6:]}'], 
                    1-self.reflectance.values[f'{self.obs_params.band}{surface.name[6:]}'])
                
            # other optics besides detector
            elif 'Detector' in surface.name:
                continue
            else:
                surface.forwardCoating = batoid.SimpleCoating(0.0, 1.0)
                surface.reverseCoating = batoid.SimpleCoating(0.0, 1.0)

    def set_detector_reflectance(self, dettype):

        for surface in self.telescope.itemDict.values():

            if isinstance(surface, batoid.Detector) and 'Detector' in surface.name:
                surface.forwardCoating = batoid.SimpleCoating(self.reflectance.values[dettype], 
                                                              1-self.reflectance.values[dettype])

    def simulate_single_star(self, fa_x, fa_y, dettype):
        
        self.set_optic_reflectance()
        self.set_detector_reflectance(dettype)
        wavelength = LSSTCamConstants.median_wavelengths[self.obs_params.band] * 1e-9

        
        rays = batoid.RayVector.asPolar(
            optic=self.telescope, wavelength=wavelength,
            theta_x=np.deg2rad(fa_x), theta_y=np.deg2rad(fa_y),
            nrad=300, naz=2000
        )
    
        rForward, rReverse = self.telescope.traceSplit(rays, minFlux=1e-4, _verbose=self._verbose)
        
        forwardFlux = np.sum([np.sum(rr.flux) for rr in rForward])
        reverseFlux = np.sum([np.sum(rr.flux) for rr in rReverse])
    
        x = np.concatenate([rr.x for rr in rForward])
        y = np.concatenate([rr.y for rr in rForward])
        flux = np.concatenate([rr.flux for rr in rForward])

        return x*1e3, y*1e3, flux, rForward 

    def simulate_fov(self):

        for i in range(self.num_stars):

            fa_x, fa_y, dettype = self.star_table['fa_x', 'fa_y', 'detector_type'][i]

            x, y, flux, ray = self.simulate_single_star(fa_x=fa_x.value, 
                                                        fa_y=fa_y.value, 
                                                        dettype=dettype)
            print(ray.path)

            
        

                
                