import asyncio
import atexit
import json
from typing import Dict

import jsons
import pathlib

from ophyd_async.core import StandardReadable, soft_signal_rw

from bact_bessyii_bluesky.model.excitation_rays import ExcitationCollection
from bact_bessyii_bluesky.plans.execute_rays import execute_rays_plan
from bact_bessyii_bluesky.plans.reinjection_diagnostic_kicker_disabled import (
    setup_reinjection,
)
from bact_bessyii_ophyd_async.devices.pp.kicker import Kicker
import bluesky
import bluesky.plans as bp
from bluesky.protocols import Reading
from bluesky.callbacks import LiveTable
from aioca import purge_channel_caches

from bact_bessyii_ophyd_async.devices.pp.topup_engine import TopUpEngine


class DAMeasure(StandardReadable):
    def __init__(self, name: str):
        with self.add_children_as_readables():
            self.hk = Kicker(ps_prefix="PKDHKR:", delay_prefix="KDHKR:", name="hk")
            self.vk = Kicker(ps_prefix="PKDVKR:", delay_prefix="KDVKR:", name="vk")
            self.topup = TopUpEngine("TOPUPCC:", target_current=5, acceptable_loss=0.5)
        super().__init__(name=name)


def main(ray_data_file_name: str):
    with open(ray_data_file_name, "rt") as fp:
        tmp = json.load(fp)
    excitation_rays = jsons.load(tmp, ExcitationCollection)

    da = DAMeasure(name="da")

    async def connect():
        await da.connect()

    asyncio.run(connect())

    RE = bluesky.RunEngine(dict(target="dynamic_aperture"))

    lt = LiveTable(
        [
            da.hk.ps.setpoint.name,
            da.vk.ps.setpoint.name,
        ]
    )
    RE.subscribe(lt)

    info_signals = dict(
        ray=soft_signal_rw(int, name="ray"),
        ray_step=soft_signal_rw(int, name="ray_step"),
    )

    def go_on(input: Dict[str, Reading]) -> bool:
        """
        check that sufficient current is still there
        """
        min_current = 0.1
        current = input[da.topup.current.name]["value"]
        return current > min_current

    reinject_plan = setup_reinjection(
        topup_device=da.topup,
        frequency_switcher=da.topup.frq_switch,
        horizontal_kicker_device=da.hk,
        vertical_kicker_device=da.vk,
    )
    (uid,) = RE(
        execute_rays_plan(
            detectors=[da],
            horizontal_excitation=da.hk.ps,
            vertical_excitation=da.vk.ps,
            info_signals=info_signals,
            rays=excitation_rays,
            reinject_plan=reinject_plan,
            go_on=go_on,
        )
    )

    print(f"{uid=}")


if __name__ == "__main__":
    atexit.register(purge_channel_caches)
    main(pathlib.Path(__name__).absolute().parent / "notebooks" / "excitation_data.json")
