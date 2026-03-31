import asyncio
import atexit
import time
import json
from typing import Dict

import jsons
import pathlib
import pprint

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
from databroker import catalog

from bact_bessyii_ophyd_async.devices.pp.topup_engine import TopUpEngine
from bact_bessyii_mls_ophyd.devices.pp.bpm_collection import BPMCollection
from bact_bessyii_mls_ophyd.devices.pp.bpm import BPM


class DAMeasure(StandardReadable):
    def __init__(self, name: str):
        with self.add_children_as_readables():
            self.hk = Kicker(ps_prefix="PKDHKR:", delay_prefix="KDHKR:", name="hk")
            self.vk = Kicker(ps_prefix="PKDVKR:", delay_prefix="KDVKR:", name="vk")
            self.topup = TopUpEngine("TOPUPCC:", target_current=2, acceptable_loss=0.5)
        super().__init__(name=name)


def main(ray_data_file_name: str):
    with open(ray_data_file_name, "rt") as fp:
        tmp = json.load(fp)
    excitation_rays = jsons.load(tmp, ExcitationCollection)
    # just the first five
    excitation_rays = ExcitationCollection(col=excitation_rays.col[:10])
    da = DAMeasure(name="da")

    bpm_col = BPMCollection(
        name="bpm",
        devices=[
            BPM(prefix="BPMZ1D8R:", name="bpmz1d8r", select_slice=slice(0, 2048)),
            BPM(prefix="BPMZ4D8R:", name="bpmz4d8r", select_slice=slice(0, 2048)),
            BPM(prefix="BPMZ5D8R:", name="bpmz5d8r", select_slice=slice(0, 2048)),
        ],
        combine_suffixes=["tbt"],
    )


    async def connect():
        await da.connect()
        await bpm_col.connect()

    asyncio.run(connect())

    RE = bluesky.RunEngine(dict(target="dynamic_aperture"))

    lt = LiveTable(
        [
            da.hk.ps.setpoint.name,
            da.hk.ps.readback.name,
            da.vk.ps.setpoint.name,
            da.vk.ps.readback.name,
            da.topup.current.name,
        ]
    )
    RE.subscribe(lt)
    db = catalog["heavy"]
    RE.subscribe(db.v1.insert)

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
        horizontal_kicker_device=da.hk.ps,
        vertical_kicker_device=da.vk.ps,
    )
    (uid,) = RE(
        execute_rays_plan(
            detectors=[da,bpm_col],
            horizontal_excitation=da.hk.ps,
            vertical_excitation=da.vk.ps,
            info_signals=info_signals,
            rays=excitation_rays,
            reinject_plan=reinject_plan,
            go_on=go_on,
            n_samples=1,
        )
    )

    print(f"{uid=}")


if __name__ == "__main__":
    # atexit.register(purge_channel_caches)
    main(pathlib.Path(__name__).absolute().parent / "examples" / "notebooks" / "excitation_data.json")
    # a chance to sleep a bit
    time.sleep(2.0)
