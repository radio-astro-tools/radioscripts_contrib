from astroquery.splatalogue import Splatalogue
from astroquery.splatalogue import utils as splatutils
from astropy.wcs import WCS
from astropy import units as u
import numpy as np

def find_lines_in_header(header, return_pixels=False, **kwargs):
    """
    Create a dictionary of line name: line position (in pixel units or
    frequency) for later extraction

    Parameters
    ----------
    header: astropy.io.fits.Header
    return_pixels: bool
        Return the line dictionary with pixel units in the header?
        Otherwises, returns frequency (in GHz)

    Examples
    --------
    >>> from astropy.io import fits
    >>> header = fits.getheader('cubefile.fits')
    >>> linedict = find_lines_in_header(header, energy_max=50,
    ...                                 energy_type='eu_k')
    """

    naxis3 = header['NAXIS3']
    wcs = WCS(header)

    xarr = np.arange(naxis3)

    r,d = wcs.wcs.crval[:2]
    frequencies = wcs.wcs_pix2world([(r,d,z) for z in xarr], 0)[:,2]
    unit = u.Unit(header['CUNIT3'])

    lines = splatutils.minimize_table(Splatalogue.query_lines(frequencies.min()*unit,
                                                              frequencies.max()*unit,
                                                              **kwargs))

    if return_pixels:
        def nearest(x):
            return np.argmin(np.abs(frequencies-x))

        linedict = {row['Species']: nearest(row['Freq']*1e9) for row in lines}
    else:
        linedict = {row['Species']: row['Freq'] for row in lines}

    return linedict
