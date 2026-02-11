import logging
from typing import Sequence

import numpy as np
from numpy import ma as ma

logger = logging.getLogger("bact-bessyii-bluesky")


def create_rays_on_turned_grid(Zm: ma.masked_array[complex], phi: Sequence[float], r: Sequence[float], threshold:float) -> Sequence[Sequence[complex]]:
    '''Select points from ZM using rays along phi and r

    But turn the grid, so it is easy to spot offset from line

    Args:
        Zm:          a masked array of complex points.
                     allows preexcluding points
        phi:         the different directions of the rays starting from the center
        r:           radial positions of the rays
        theshold ... maximum distance to accept as deviation
    '''
    phi = np.atleast_1d(phi)
    r = np.atleast_1d(r)

    Z = Zm.data.copy()
    mask = Zm.mask.copy()

    # maximum numbers to take in one ray
    n_max = max(Z.shape)
    rays = []

    for p in phi:
        # Turn the data so that offsets are easy to identify
        # Mask already selected points .
        # In the beginning mask should be set to the points outside the largest circle
        Z_rotated = ma.masked_array(Z * np.exp(-p * 1j), mask=mask)

        # find points which are nearest to ideal line
        dZ = np.absolute(Z_rotated.imag)
        dZr = dZ.ravel()

        args = dZr.argsort()
        # only use those args for which the distance is below some threshold
        # and not more than points in one dimension
        max_points = min(np.sum(dZr < threshold), n_max)
        if not max_points:
            continue
        args = args[:max_points]

        # select the points
        Zsel = Z.ravel()[args]
        # Sort the points by distance from center
        Zsel = Zsel.tolist()
        Zsel = [z for z in Zsel if z is not None]
        try:
            Zsel.sort(key=np.absolute)
        except Exception as exc:
            logger.error(f'{Zsel=}: {exc=}')
            raise exc
        Zsel = np.array(Zsel)
        rays.append(Zsel)

        # Mask already used points
        maskr = mask.ravel()
        maskr[args] = True
        mask = maskr.reshape(mask.shape)

    return rays, mask



def create_rays_on_grid(Zm: ma.masked_array[complex], phi: Sequence[float], r: Sequence[float], threshold:float) -> Sequence[Sequence[complex]]:
    '''Select points from ZM using rays along phi and r

    Args:
        Zm:          a masked array of complex points.
                     allows preexcluding points
        phi:         the different directions of the rays starting from the center
        r:           radial positions of the rays
        theshold ... maximum distance to accept as deviation
    '''
    phi = np.atleast_1d(phi)
    r = np.atleast_1d(r)

    Z = Zm.data.copy()
    mask = Zm.mask.copy()

    rays = []

    for p in phi:
        # Calculate in the complex
        zt = r * np.exp(p * 1j)

        # Mask already selected points
        # In the beginning mask should be set to the points outside the largest circle
        Zm = ma.masked_array(Z, mask=mask)
        Zmr = Zm.ravel()

        # distance to the points along the ray
        dZ = Zmr[np.newaxis, :] - zt[:, np.newaxis]
        dZa = np.absolute(dZ)

        # nearest point
        args = dZa.argmin(axis=1)

        # distance of selected to original point
        dZsel = dZ[np.arange(zt.shape[0]), args]
        dZsela = np.absolute(dZsel)

        # only use those args for which the distance is below some thresod
        args = args[dZsela < threshold]

        # avoid repetition of identical points
        t_args = list(set(args.tolist()))
        Zsel = Zmr[t_args]

        # Sort the points by distance from center
        Zsel = Zsel.tolist()
        Zsel = [z for z in Zsel if z is not None]
        try:
            Zsel.sort(key=np.absolute)
        except Exception as exc:
            logger.error(f'{Zsel=}: {exc=}')
            raise exc
        Zsel = np.array(Zsel)
        rays.append(Zsel)

        # Mask already used points
        maskr = mask.ravel()
        maskr[args] = True
        mask = maskr.reshape(mask.shape)

    return rays, mask
