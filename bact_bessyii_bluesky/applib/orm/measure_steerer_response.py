"""measure quadrupole response: for BESSY II

"""
# from databroker import catalog

from bact_bessyii_bluesky.live_plot import orbit_plots
from bact_bessyii_mls_ophyd.devices.process.counter_sink import CounterSink
from bact_bessyii_ophyd.devices.pp.steerers.steerer_muxer import SteerersCollection
from bact_bessyii_ophyd.devices.pp.bpm.bpm import BPM

import bluesky.plans as bp
from bluesky import RunEngine
from bluesky.callbacks import LiveTable

import numpy as np
from cycler import cycler
from functools import partial



def main(
    prefix,
    currents,
    machine_name,
    catalog_name,
    measurement_name,
    magnet_names=["Q3M2T8R"],
    try_run=False,
):
    # async def measure():

    # BESSSY II ...
    bpm_devs = BPM(prefix + "MDIZ2T5G", name="bpm")
    # BESSY II needs the hardware multiplexer ...

    # MLS has separate power converters these are collected as a software device
    mux = SteerersCollection(prefix, name="mux")
    # Measure the tune ... a quantity directly linked to the change of the quadrupole
    # Typically rather straightforward to measure
    # tn = tune.Tunes(prefix + "TUNEZRP", name="tn")
    cs = CounterSink(name="cs")

    steerer_names = mux.get_element_names()

    lt = LiveTable(
        [
            mux.sel.selected.name,
            "mux_sel_p_setpoint",
            "mux_sel_r_setpoint",
            "mux_sel_p_readback",
            "mux_sel_r_readback",
            cs.name,
        ],
        default_prec=10,
    )

    plot = orbit_plots.plots(
        magnet_name=mux.sel.selected.name,
        ds=None,
        x_pos="/".join(["bpm_elem_data", "x"]),
        y_pos="/".join(["bpm_elem_data", "y"]),
        y_scale=1e6,
        reading_count=cs.setpoint.name,
    )

    if not mux.connected:
        mux.wait_for_connection(timeout=10)

    cyc_magnets = cycler(mux, steerer_names)
    currents = np.array([0, -1, 0, 1, 0])
    cyc_currents = cycler(mux.sel, currents)
    cyc_count = cycler(cs, range(3))
    cmd = partial(bp.scan_nd, [bpm_devs], cyc_magnets * cyc_currents * cyc_count)
    cbs = [lt] + plot  # + lp

    md = dict(
        machine=machine_name,  # "BessyII"
        nickname="bba",
        measurement_target=measurement_name,  # "beam_based_alignment",
        target="beam based alignemnt test",
        comment="currently only testing if data taking works",
    )
    RE = RunEngine(md)
    if catalog_name:
        from databroker import catalog
        db = catalog[catalog_name]  # "heavy_local"]
        RE.subscribe(db.v1.insert)

    # hidden side effect: I guess a run engine must exist to be able to use that?
    # see that limits are implemented in the digital twin
    # check_limits(cmd())
    uids = RE(cmd(), cbs)

    print(f"Measurement uid {uids}")
    return uids
