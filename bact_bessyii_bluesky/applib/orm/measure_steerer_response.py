"""measure quadrupole response: for BESSY II

"""
from bluesky.simulators import check_limits

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
import logging
import pprint

logger = logging.getLogger("bessyii-bluesky")


def main(
    prefix,
    currents,
    machine_name,
    catalog_name,
    measurement_name,
    magnet_names=["VS2M2T2R", "VS2M2T4R"],
    try_run=False,
):

    # Beam position monitors
    bpm_devs = BPM(prefix + "MDIZ2T5G", name="bpm")
    # a muxer in software
    mux = SteerersCollection(prefix, name="mux")
    if not mux.connected:
        # would be handled by run engine / presumably stage when starting
        # but with so many channels the standard timeout is too short
        mux.wait_for_connection(timeout=5)

    # count the readings: simplifies analysis later on
    cs = CounterSink(name="cs")

    # Set up the live table: plot what you want to see online
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

    m2mm = 1e3
    plot = orbit_plots.plots(
        magnet_name=mux.sel.selected.name,
        ds=None,
        x_pos="/".join(["bpm_elem_data", "x"]),
        y_pos="/".join(["bpm_elem_data", "y"]),
        x_scale=1,
        y_scale=m2mm,
        reading_count=cs.setpoint.name,
    )

    steerer_names = mux.get_element_names()
    if try_run:
        for name in magnet_names:
            # only use the names of the magnets specified on the command line
            if name not in steerer_names:
                logger.error("steerer names %s", steerer_names)
                raise AssertionError(f"{name} not in steerer_names")
        steerer_names = magnet_names

    # store the value the power converter say the current has now
    # in case of failure it should be set back to that one 

    for name in steerer_names:
        pc = getattr(mux.power_converters, name)
        rb = pc.r.setpoint.get()
        # current value as offset and reset value
        pc.r.configure(dict(rv=rb, set_back=True))
        pc.configure(dict(offset=rb))

    cyc_magnets = cycler(mux, steerer_names)

    currents = np.asarray(currents)
    cyc_currents = cycler(mux.sel, currents)
    cyc_count = cycler(cs, range(3))
    cmd = partial(bp.scan_nd, [bpm_devs], cyc_magnets * cyc_currents * cyc_count)
    cbs = [lt] + plot  # + lp

    md = dict(
        machine=machine_name,  # "BessyII"
        nickname="orm",
        measurement_target=measurement_name,  # "beam_based_alignment",
        target="orbit response measurement",
        comment="demonstration run",
    )
    RE = RunEngine(md)
    if catalog_name:
        from databroker import catalog
        db = catalog[catalog_name]
        RE.subscribe(db.v1.insert)


    # hidden side effect: I guess a run engine must exist to be able to use that?
    # see that limits are implemented in the digital twin
    check_limits(cmd())
    uids = RE(cmd(), cbs)

    print(f"Measurement uid {uids}")
    return uids
