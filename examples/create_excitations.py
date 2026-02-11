from typing import Sequence

import numpy as np
import numpy.ma as ma
from bact_bessyii_bluesky.applib.utils.create_rays_on_grid import create_rays_on_grid, create_rays_on_turned_grid
from bact_bessyii_bluesky.applib.utils.produce_in_between import produce_in_between
from bact_bessyii_bluesky.model.excitation_rays import Excitation, ExcitationRay, ExcitationCollection


def convert_complex_ray_to_excitations(ray: Sequence[complex]) -> Sequence[Excitation]:
    return [Excitation(float(p.real), float(p.imag)) for p in ray]


def convert_complex_rays_to_excitation_rays(rays: Sequence[Sequence[complex]]) -> Sequence[ExcitationRay]:
    return [ExcitationRay(ray=convert_complex_ray_to_excitations(ray)) for ray in rays]


def main():
    angles = [0, 90] + [angle for angle in produce_in_between(0, 90, maxdepth=5)]
    angles = np.array(angles)

    x = np.concatenate([
        np.linspace(0, 3, 3 * 2, endpoint=True),
        np.linspace(3, 5, 2 * 4 + 1)
    ])
    y = np.concatenate([
        np.linspace(0, 3, 3 * 2, endpoint=True),
        np.linspace(3, 5, 2 * 4 + 1)
    ])
    X, Y  = np.meshgrid(x,y)
    Z_grid = X + Y * 1j
    radius = 4.5
    mask = np.abs(Z_grid) > radius
    Zm = ma.masked_array(Z_grid, mask=mask)
    mask = np.array(Z_grid.shape, dtype=bool)
    print(Z_grid.astype(int))
    r = np.linspace(0, 5, num=101)
    rays, remaning_points = create_rays_on_turned_grid(
        Zm, angles/180.0*np.pi, r, threshold=0.05
    )

    rays = convert_complex_rays_to_excitation_rays(rays)
    rays
    ec = ExcitationCollection(col=rays)
    ec
    rays

if __name__ == "__main__":
    main()