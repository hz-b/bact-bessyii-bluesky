import logging
from dataclasses import asdict
from typing import Dict, Any, Callable, Mapping

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.protocols import Reading

from ..model.excitation_rays import ExcitationCollection, ExcitationRay

log = logging.getLogger("bact-bessyii-bluesky")


def execute_rays_plan(
    detectors,
    horizontal_excitation,
    vertical_excitation,
    info_signals,
    rays: ExcitationCollection,
    reinject_plan,
    go_on: Callable[[Mapping[str, Reading]], bool],
    md: None,
):
    """ """
    _md = md or {}
    _md["ray-excitations"] = asdict(rays)
    # Check that these are available
    assert info_signals["ray"]
    assert info_signals["ray_step"]

    @bpp.stage_decorator(
        list(detectors) + [horizontal_excitation, vertical_excitation] + list(info_signals)
    )
    @bpp.run_decorator(md=_md)
    def inner():
        yield from dynamic_aperture_rays_plan(
            detectors=detectors,
            horizontal_excitation=horizontal_excitation,
            vertical_excitation=vertical_excitation,
            info_signals=info_signals,
            rays=rays,
            reinject_plan=reinject_plan,
            go_on=go_on,
        )

    r = yield from inner()
    return r


def dynamic_aperture_rays_plan(
    detectors,
    horizontal_excitation,
    vertical_excitation,
    info_signals: Dict[str, Any],
    rays: ExcitationCollection,
    go_on: Callable[[Mapping[str, Reading]], bool],
    reinject_plan,
):
    for cnt, ray in enumerate(rays.col):
        yield from bps.mv(info_signals["ray"], cnt)
        yield from reinject_plan()
        yield from dynamic_aperture_single_ray_plan(
            detectors=detectors,
            horizontal_excitation=horizontal_excitation,
            vertical_excitation=vertical_excitation,
            info_signals=info_signals,
            ray=ray,
            go_on=go_on,
        )


def dynamic_aperture_single_ray_plan(
    detectors,
    horizontal_excitation,
    vertical_excitation,
    info_signals: Dict[str, Any],
    ray: ExcitationRay,
    go_on: Callable[[Mapping[str, Reading]], bool],
    n_samples: int = 1,
    wait_after_set: float = 0.0,
    wait_between_sample: float = 0.0,
):
    """Execute a plan consisting of a single ray

    Warning:
        reinjection only happens after the current is lost

    Todo:
        enforce consistent naming of the kickers and power converters?
    """

    for cnt, excitation in enumerate(ray.ray):
        yield from bps.mv(
            info_signals["ray_step"],
            cnt,
            horizontal_excitation,
            excitation.horizontal,
            vertical_excitation,
            excitation.vertical,
        )
        yield from bps.sleep(wait_after_set)
        for sample in range(n_samples):
            if sample > 0:
                yield from bps.sleep(wait_between_sample)
            r = yield from bps.trigger_and_read(detectors)
            if not go_on(r):
                return


__all__ = ["execute_rays_plan"]