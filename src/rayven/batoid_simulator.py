from astropy.table import QTable

class BatoidSimulator:

    def __init__(self, star_table, scaling):

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