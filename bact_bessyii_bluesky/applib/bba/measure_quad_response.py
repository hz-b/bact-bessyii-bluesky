"""measure quadrupole response: for BESSY II

"""
from functools import partial
import bluesky.plans as bp
import matplotlib.pyplot as plt
import numpy as np
from bact_bessyii_mls_ophyd.devices.process.counter_sink import CounterSink
from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from cycler import cycler
from databroker import catalog
from bact_bessyii_bluesky.live_plot import orbit_plots
from bact_bessyii_ophyd.devices.pp import bpm, multiplexer

import concurrent.futures
executor = concurrent.futures.ThreadPoolExecutor()

def main(prefix, currents,machine_name,catalog_name, measurement_name,try_run=False):
    # async def measure():

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
    # test hack ...
    quad_names = ["q3m2t8r"]
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
    if False:
        bpm_read = bpm_devs.read()
        plot_data = [[bpm_data[plane]['pos_raw'] for plane in ("x", "y")]
                     for bpm_data in bpm_read["bpm_elem_data"]['value']]
        plot_data = np.array(plot_data)
        # a test plot
        fig, test_ax = plt.subplots(2, 1, sharex=True)
        ax_x, ax_y = test_ax
        pscale = 1000
        ax_x.plot(plot_data[:,0] * pscale)
        ax_y.plot(plot_data[:,1] * pscale)
        ax_x.set_label("x [mm]")
        ax_y.set_label("y [mm]")

    # # Iterate over the elements in your array and collect the data
    # for elem in bpm_read["bpm_elem_data"]['value']:
    #     x_pos = elem['x']['pos_raw']
    #     # Add the data to the plot_data list
    #     plot_data.append((x_pos, y_pos))
    # # Plot the data from the array
    # lplt = plt.plot(plot_data)
    # plot_list = []
    # for elem in bpm_read["bpm_elem_data"]['value']:
    plot = orbit_plots.plots(magnet_name=mux.selected_multiplexer.setpoint.name,
                             ds=None,
                             x_pos="/".join(["bpm_elem_data", "x"]),
                             y_pos="/".join(["bpm_elem_data", "y"]),
                             y_scale = 1e6,
                             # x_pos=["bpm_elem_data", "value", "x", "pos_raw"],
                             #y_pos=["bpm_elem_data", "value", "y", "pos_raw"],
                             reading_count=cs.setpoint.name
    )
    #    plot = orbit_plots.plots(magnet_name=None,
    #                          ds=elem['name'],
    #                          x_pos=elem['x']['pos_raw'],
    #                          y_pos=elem['y']['pos_raw'],
    #                          reading_count=cs.setpoint.name)
    #     plot_list.append(plot)

    if not mux.connected:
        mux.wait_for_connection(timeout=10)
    print(mux.describe())

    cyc_magnets = cycler(mux.selected_multiplexer, quad_names)
    currents = np.array([0, -1, 0, 1, 0]) * 2
    cyc_currents = cycler(mux.power_converter, currents)
    cyc_count = cycler(cs, range(3))
    cmd = partial(bp.scan_nd, [bpm_devs], cyc_magnets * cyc_currents * cyc_count)
    cbs = [lt ] + plot  # + lp

    db = catalog[catalog_name ]#"heavy_local"]

    md = dict(machine=machine_name #"BessyII"
              , nickname="bba", measurement_target= measurement_name,#"beam_based_alignment",
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
    return uids
    # return anyio.to_thread(measure)
# async def run_sync_synchronously(func, *args, **kwargs):
#     return await anyio.to_thread.run_sync(func, *args, **kwargs)