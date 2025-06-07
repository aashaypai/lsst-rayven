from astropy import units as u
from dataclasses import dataclass

@dataclass
class DataProduct:

    name: str
    data: any
    units: str = None