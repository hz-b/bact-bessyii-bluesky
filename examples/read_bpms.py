import matplotlib.pyplot as plt
from bact_mls_ophyd.devices.pp import bpm
from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from bact2.bluesky.live_plot import orbit_plots
from databroker import catalog
from event_model import RunRouter
import bluesky.plans as bp
from cycler import cycler
import numpy as np
from functools import partial
from bact2.databroker.msgpack import factories
import os


def main():
    prefix = "Pierre:DT:"
    # bpm = BPM(prefix + "MDIZ2T5G", name="bpm")
    bpm_devs = bpm.BPM(prefix+"BPMZ1X003GP", name="bpm")
    if not bpm_devs.connected:
        bpm_devs.wait_for_connection()

    data = bpm_devs.read()
    lt = LiveTable(
        [
            bpm_devs.count.name
        ]
    )
    md = dict(
        machine="MLS",
        nickname="bpm_test",
        measurement_target="read bpm data",
        target="see if bpm data can be read by RunEngine",
        comment="currently only testing if data taking works",
    )

    RE = RunEngine(md)
    lps = orbit_plots.plots(magnet_name="no_name", ds="bpm_ds", x_pos="bpm_x_pos_raw", y_pos="bpm_y_pos_raw",
                            reading_count="bpm_count", log=RE.log)

    if True:
        db = catalog["heavy"]
        RE.subscribe(db.v1.insert)
    else:
        savedir = path = os.path.join(os.environ["HOME"], "data", "bpm", "experiment")
        print(savedir)
        # return
        rr = RunRouter(
            [partial(factories, savedir)]
        )
        RE.subscribe(rr)

    # RE.subscribe(db.v1.insert)
    uids = RE(bp.count([bpm_devs], 5), [lt]  # + lps
              )
    print(f"run uids {uids}")


if __name__ == "__main__":
    plt.ion()
    try:
        main()
    except:
        raise
    else:
        plt.ioff()
        plt.show()
