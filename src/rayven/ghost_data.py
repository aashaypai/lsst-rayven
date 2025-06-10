from astropy import units as u
from dataclasses import dataclass, field
from batoid import RayVector
from typing import List
import numpy as np
@dataclass
class Ghost:

    name: str
    ray: RayVector
    x: List[float] = field(default_factory=list)
    y: List[float] = field(default_factory=list)
    flux: List[float] = field(default_factory=list)
    
@dataclass
class GhostBundle:
    ghosts: List[Ghost] = field(default_factory=list)
    
    def __getitem__(self, index):
        return self.ghosts[index]

    def __len__(self):
        return len(self.ghosts)
        
    @property
    def x(self):
        return np.concatenate([ghost.x for ghost in self.ghosts])

    @property
    def y(self):
        return np.concatenate([ghost.y for ghost in self.ghosts])

    @property
    def flux(self):
        return np.concatenate([ghost.flux for ghost in self.ghosts])

    @property
    def total_flux(self):
        return np.sum(self.flux)
    

    
    
    