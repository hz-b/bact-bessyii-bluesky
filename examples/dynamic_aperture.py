import asyncio, inspect

from ophyd_async.core import StandardReadable
from bact_bessyii_ophyd_async.devices.pp.kicker import Kicker
from bact_bessyii_ophyd_async.devices.raw.delay import Delay
import bluesky
import bluesky.plans as bp
from bluesky.callbacks import LiveTable
from aioca import purge_channel_caches


class DAMeasure(StandardReadable):
    def __init__(self, name:str):
        with self.add_children_as_readables():
            self.hk = Kicker(ps_prefix="PKDHKR:", delay_prefix="KDHKR:", name="hk")
            self.vk = Kicker(ps_prefix="PKDVKR:", delay_prefix="KDVKR:", name="vk")
        super().__init__(name=name)


        # hk = Cpt(HKicker, name='hk')
        # vk = Cpt(VKicker, name='vk')


def main():

    
    da = DAMeasure(name="da")

    async def connect():
        await da.connect()
    asyncio.run(connect())

    RE = bluesky.RunEngine(dict(target="dyamic_aperture"))
    # uid, = RE(bp.count([da], num=2))
    # print(f"{uid=}")

    lt = LiveTable([
        da.hk.ps.setpoint.name,
        da.vk.ps.setpoint.name,
    ])
    RE.subscribe(lt)
    uid, = RE(bp.scan([da], da.vk.ps, 0, 10, num=11))
    print(f"{uid=}")


    # pie_planned_scans = xr.open_dataarray('pie_planned_scans.nc')
    # rays = pie_planned_scans


#    if False:
#        # hk = Cpt(HKicker, name='hk')
#        # vk = Cpt(VKicker, name='vk')
#        # lb = Cpt(libera.LiberaBox, name='lb')
#
#        lt  = Cpt(life_time.LifeTime, name = 'lt')
#        ltm = Cpt(lt_pp.LifetimeDevice, name = 'lt_dev')
#
#        # Some hints problem in counter sink?
#        # cs = Cpt(CounterSink, name="cur_reads", delay=0)
#
#        topup = Cpt(topup_engine.TopUpEngine, name='topup')
#
#        #: finished for this setting
#        finished_ray = Cpt(Signal,name='finished_ray', value=False)
#
#        #: finished for this setting
#        finished = Cpt(Signal, name='finished', value=False)
#
#        #: reinjection number ... book keeping of how often it was made
#        #: should
#        inj_cnt = Cpt(Signal, name='inj_cnt', value=0)
#
#        #: sextupole power converters
#        # sp = SextupolePowerconverters(name='sc')
#        # def trigger(self):
#        #     # stat2 = self.lb.trigger()
#        #     #return stat2
#        #
#        #     stat = self.ltm.trigger()
#        #     return stat
#        #     return AndStatus(stat, stat2)
#
#    dam = DAMeasure(name='dam')
#    # new deirection
#
#    # def reset_stat(*args, **kwargs):
#    #     RE.log.warning(f'Resetting statistics args {args} kwargs {list(kwargs.keys())}')
#    #     dam.finished.put(False)
#    #     dam.ltm.resetCurrentReadings()
#    #
#    # def finished_scan(*args, **kwargs):
#    #     RE.log.warning(f'Resetting scan args {args} kwargs {list(kwargs.keys())}')
#    #     dam.finished.put(False)
#    #     dam.ltm.resetCurrentReadings()
#    # print(dam.kicker.phi.event_types)
#    # print(dam.kicker.r.event_types)
#    # print(dam.cs.event_types)
#    # return
#
#    # dam.kicker.phi.subscribe(finished_scan,
#    #                          dam.kicker.phi.SUB_START
#    # )
#    # #return
#    # dam.kicker.phi.subscribe(reset_stat, dam.kicker.phi.SUB_START)
#    # dam.kicker.r.subscribe(reset_stat, dam.kicker.r.SUB_START)
#
#    if not dam.connected:
#        dam.wait_for_connection()
#
#    for mon in dam.ltm.current_monitors:
#       mon.min_readings.put(3)
#       mon.readings_to_sum.put(100)
#
#    # Harmonic sextupoles
#    # sext_power_converters = [
#    #     dam.sp.S3PDR, dam.sp.S3PTR,
#    #     dam.sp.S4PDR, dam.sp.S4PTR,
#    #
#    #     dam.sp.S3PD1R, dam.sp.S4PD1R,
#    #
#    #     dam.sp.S3P1T6R, dam.sp.S4P1T6R,
#    #     dam.sp.S3P2T6R, dam.sp.S4P2T6R
#    # ]
#    #
#    # for pc in sext_power_converters:
#    #   pc.settle_time =.4
#    #   pc.timeout = 2 * 6 * 10
#
#
#    RE = RunEngine({})
#    cat = None
#    # With many files that gets really slow
#    db = catalog['heavy']
#    # cat = catalog['bbfbc1c']
#    # better a mongodb ....
#    # cat = catalog['light']
#    RE.subscribe(db.v1.insert)
#
#
#    dam.log = RE.log
#    dam.kicker.log = RE.log
#    dam.ltm.log = RE.log
#    dam.ltm.life_time.log = RE.log
#
#    # Should be in single bunch mode ....
#    dam.topup.target_current.put(1.0)
#    dam.topup.acceptable_loss.put(.1)
#
#    # 1 Hz who knows where it was left
#    dam.topup.frequency.put(0)
#
#    ## # half a herz ...
#    ## dam.topup.req_inj_freq.put(1)
#    ## # setup for testing script
#    dam.ltm.min_err.put(1)
#    dam.ltm.min_est.put(3)
#    ##
#    ## # need to fix pseudopos
#    ## hk = dam.kicker.hk
#    ## vk = dam.kicker.vk
#
#    f, axes = plt.subplots(3, 1, sharex=True, figsize=[8,6])
#    ax1, ax2, ax3 = axes
#
#    f2, axes = plt.subplots(2, 1, sharex=True, figsize=[8,6])
#    ax_x, ax_y  = axes
#
#    f3, ax = plt.subplots(1, 1, sharex=True, figsize=[8,6])
#
#    print("lt", list(dam.ltm.describe().keys()))
#    
#    lt_avg_name = dam.ltm.name
#    lt_err_avg_name = dam.ltm.life_time.lt_err.name
#    lt_est_avg_name = dam.ltm.life_time.lt.name
#
#    
#    lt = LiveTable([
#        dam.ltm.beam_current_triggered.readback,
#        # dam.kicker.r.setpoint, dam.kicker.phi.setpoint,
#        dam.kicker.hk.ps.setpoint, dam.kicker.vk.ps.setpoint,
#        lt_est_avg_name, lt_avg_name, lt_err_avg_name,
#        # dam.ltm.below_min_err.name,
#        # dam.ltm.above_min_est.name
#    ])
#
#    # x for the libera boxes
#
#
#    scatter = LiveScatter(
#        x=dam.kicker.hk.ps.setpoint.name,
#        y=dam.kicker.hk.ps.setpoint.name,
#        I=lt_est_avg_name,
#        ax=ax,
#        cmap="viridis",
#        s=30
#    )
#    lp =  [
#        LivePlot(dam.kicker.hk.ps.setpoint.name, x='time', ax=ax1, legend_keys = ['x']),
#        LivePlot(dam.kicker.vk.ps.setpoint.name, x='time', ax=ax2, legend_keys = ['y']),
#        scatter,
#        #LivePlot(dam.kicker.r.setpoint.name,  x='time', ax=ax3, legend_keys = ['r']),
#        # PlotLineVsIndex(dam.lb.lrg_buf.x.name, ax=ax_x, legend_keys=['x']),
#        # PlotLineVsIndex(dam.lb.lrg_buf.y.name, ax=ax_y, legend_keys=['y'])
#    ]
#    cbs = [lt] + lp
#
#    det = [dam]
#
#    # sufficent_current = suspenders.SuspendFloor(topup_cc, .5, resume_thresh=11)
#    # RE.install_suspender(sufficent_current)
#
#    # Life time estimate does not seem to work for single bunch current
#    # lets go to 5 values
#    n_current_readings = 5
#    r_vals =  np.linspace(3.5, 6, num=int((6 - 3.5) * 20 + 1))
#    # r_steps = cycler(dam.kicker.r, r_vals)
#
#    phi_vals =  np.linspace(0.0, np.pi/2, num=19)
#    phi_vals =  np.linspace(0.0, np.pi/2, num=19)[:-1] + 2.5/180*np.pi
#    # phi_steps = cycler(dam.kicker.phi, phi_vals)
#
#
#    md = {
#        # 'purpose'  : 'preparation for taking overnight data',
#        # 'purpose'  : 'taking data for comparison to original bba evaluation',
#        'purpose'  : 'dynamic aperture scan along different radii',
#        'measurement_type' : 'scaning dynamic aperture with harmonic sextupoles off',
#        'nickname' : 'da_scan',
#        'comment' : '''more or less constant phi. Trying to match rectangular grid.
#        Chromaticity in x and y supposed to be one (like last time) Harmonic sextupoles to minimum current.'''
#    }
#
#    first_run = True
#    def per_step(detectors, step, pos_cache):
#        nonlocal first_run
#        f = per_step_da_scan
#        yield from f(detectors, step, pos_cache, first_run=first_run,
#                     device=dam, lifetime=dam.ltm, log=RE.log,
#                     n_current_readings = n_current_readings,
#                     sextupoles=None
#                     # sextupoles=sext_power_converters,
#        )
#        first_run = False
#
#    # all_steps =  (phi_steps *  r_steps) * n_current_readings
#    # cmd = functools.partial(bp.scan_nd, det, all_steps, per_step=per_step)
#    # check_limits(cmd())
#
#    if False:
#        print('Starting for test of chroma')
#
#        x_steps = cycler(dam.kicker.hk, [3,] * 5)
#        y_steps = cycler(dam.kicker.vk, [0,] * 5)
#
#        all_steps = x_steps + y_steps
#
#        cmd = functools.partial(bp.scan_nd, det, all_steps, per_step=per_step)
#        uids = RE(cmd(), cbs, comment2='test of chromaticity', **md)
#        return
#
#    print('Starting iterating over rays')
#    print(rays.coords)
#    for ray_num in rays.coords['ray'].values:
#        # if ray_num <= 31:
#        #    continue
#
#        print(f'Working on ray {ray_num}')
#        ray_data = rays.sel(dict(ray=ray_num))
#        valid = ray_data.sel(dict(coor='valid'))
#        items = np.arange(np.sum(valid))
#        phi = ray_data.sel(dict(coor='phi', num=items)).values
#        r = ray_data.sel(dict(coor='r', num=items)).values
#        x = ray_data.sel(dict(coor='x', num=items)).values
#        y = ray_data.sel(dict(coor='y', num=items)).values
#
#        x_steps = cycler(dam.kicker.hk, x)
#        y_steps = cycler(dam.kicker.vk, y)
#
#        # print(x)
#        # print(y)
#        # return
#
#        all_steps = x_steps + y_steps
#
#        cmd = functools.partial(bp.scan_nd, det, all_steps, per_step=per_step)
#        first_run = True
#        uids = None
#        RE.log.warning('Starting measurement')
#        print(f'Measuring ray {ray_num=} using {len(x)} steps:'
#              f' x: {x.min()}..{x.max()} y: {y.min()}..{y.max()}')
#        # print(f' x: {x}')
#        # print(f' y: {y}')
#        try:
#            uids = RE(cmd(), cbs, ray_num=ray_num, **md)
#            pass
#        finally:
#            print(f'Ray number {ray_num} measurement uids {uids}')
#
#    print('Done interating rays')


if __name__ == '__main__':
    main()
    purge_channel_caches
    # plt.ion()
    # try:
    # except Exception as e:
    #     print(f'Failed!: {e}')
    #     plt.ioff()
    #     raise e
    # else:
    #     plt.ioff()
    #     plt.show()
    # print('Close plot window for stopping progam')
