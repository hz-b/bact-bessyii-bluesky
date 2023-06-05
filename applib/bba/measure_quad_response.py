"""measure quadrupole response: for BESSY II

"""
from functools import partial

import bluesky.plans as bp
import matplotlib.pyplot as plt
import numpy as np
# to be replaced by a proper reimplementation
# from bact2.ophyd.devices.raw import multiplexer
from bact2.ophyd.utils.preprocessors.CounterSink import CounterSink
from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from cycler import cycler
from databroker import catalog

from custom.bessyii.ophyd.bact_bessy_ophyd.devices.pp import bpm, multiplexer


def main(*, try_run=False, prefix=""):
    # BESSSY II ...
    bpm_devs = bpm.BPM(prefix + "MDIZ2T5G", name="bpm")
    # BESSY II needs the hardware multiplexer ...
    mux = multiplexer.Multiplexer(prefix=prefix, name="mux")
    # MLS has separate power converters these are collected as a software device
    # mux = quadrupoles.QuadrupolesCollection(name="mux")
    # Measure the tune ... a quantity directly linked to the change of the quadrupole
    # Typically rather straightforward to measure
    # tn = tune.Tunes(prefix + "TUNEZRP", name="tn")
    cs = CounterSink(name="cs")

    quad_names = mux.get_element_names()
    if try_run:
        quad_names = quad_names[:2]
    lt = LiveTable(
        [
            mux.selected_multiplexer.setpoint.name,
            mux.power_converter.readback,
            "qc_sel_p_setpoint",
            "qc_sel_r_setpoint",
            "qc_sel_p_readback",
            "qc_sel_r_readback",
            cs.name,
        ],
        default_prec=10
    )

    # lp = orbit_plots.plots(magnet_name=mux.selected_multiplexer.selected.name,
    #                        ds=bpm_devs.ds.name,
    #                        # ds = bpm_devs.x.pos_raw.name,
    #                        x_pos=bpm_devs.x.pos.name,
    #                        y_pos=bpm_devs.y.pos.name,
    #                        reading_count=cs.setpoint.name,
    #                        )

    if not mux.connected:
        mux.wait_for_connection()
    print(mux.describe())

    cyc_magnets = cycler(mux.selected_multiplexer, quad_names)
    currents = np.array([0, -1, 0, 1, 0]) * 5e-1
    cyc_currents = cycler(mux.power_converter, currents)
    cyc_count = cycler(cs, range(3))
    cmd = partial(bp.scan_nd, [bpm_devs], cyc_magnets * cyc_currents * cyc_count)
    cbs = [lt]  # + lp

    db = catalog["heavy"]

    md = dict(machine="BessyII", nickname="bba", measurement_target="beam_based_alignment",
              target="beam based alignemnt test",
              comment="currently only testing if data taking works"
              )
    RE = RunEngine(md)
    RE.subscribe(db.v1.insert)

    # hidden side effect: I guess a run engine must exist to be able to use that?
    # see that limits are implemented in the digital twin
    # check_limits(cmd())
    uids = RE(cmd(), cbs)

    print(f"Measurement uid {uids}")


if __name__ == "__main__":
    plt.ion()
    try:
        main(try_run=True, prefix="Pierre:DT:")
    except:
        raise
    else:
        plt.ioff()
        plt.show()
