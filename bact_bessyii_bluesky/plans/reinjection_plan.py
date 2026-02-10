import logging

logger = logging.getLogger("bact-bessyii-bluesky")


def reinject_current(topup, ramp_voltage: bool=True):
    log.warning(f'Reinjecting current as requested ')
    
    
    if ramp_voltage:
        hk_set = hk.ps.setpoint.get()
        vk_set = vk.ps.setpoint.get()
        
        # set kickers to zero
        ramp_targets = [hk.ps, 0, vk.ps, 0]
        
        # # set sextupoles to nominal values
        # ramp_targets = [(pc, pc.store.get()) for pc in sextupoles]
        # ramp_targets = list(itertools.chain(*ramp_targets))
        
        yield from bps.mv(*ramp_targets)
        yield from bps.checkpoint()
        
    else:
        # Just deactivate the kicker
        yield from bps.mv(hk.delay.switch, 0, vk.delay.switch, 0)

    # reinject current
    yield from bps.mv(topup, True)


def per_step_da_scan(detectors, step, pos_cache, *, first_run, device,
                     lifetime, sextupoles, n_current_readings, log):
    '''
    '''

    motors = list(step.keys())
    dam, = detectors
    # topup engine
    topup = device.topup
    hk = device.kicker.hk
    vk = device.kicker.vk
    topup_cc = lifetime.beam_current_triggered.readback


    # logger.warning(f"per da scan : using motors {motors}")
    # logger.warning(f"per da scan : using motors {detectors}")
    do_inject = False
    # ensure a valid not too old current reading ...
    if first_run:
        # First run ensure a reading
        log.warning('First run ...')
        yield from bps.checkpoint()
        r = yield from bps.trigger_and_read(list(detectors) + list(motors))

        yield from bps.mv(device.finished, 0)
        lifetime.resetCurrentReadings()

        # Reset finshed we did not start yet
        do_inject = True

    yield from bps.checkpoint()

    kicker_pos = dict(x=step[hk], y=step[vk])

    last_kicker_pos_x = pos_cache[hk]
    last_kicker_pos_y = pos_cache[vk]

    # Not in this case ...
    if kicker_pos['x'] != last_kicker_pos_x or kicker_pos['y'] != last_kicker_pos_y:
        # Single ray no reset
        pass
        # yield from bps.mv(device.finished, 0)
        # lifetime.resetCurrentReadings()

    # Already done for this motor setting
    # This must only be executed after the motor was set
    # The motor setting is responsibe for resetting the statistics
    if device.finished.get():
        return
    if device.finished_ray.get():
        return

    test_current = topup_cc.get()

    # Assuming that each ray is run in one run.
    # Inject in the beinning but not later on
    # low_current = .5
    # if test_current < low_current:
    #     log.warning(f'Reinjecting as current {test_current} below {low_current}')
    #    do_inject = True

        # Some strange results possible
        # e.g. yet a bunch to be delivered ...

        # set the kickers back
        if ramp_voltage:
            # set sextupoles to some minimal values
            # ramp_targets = [(pc, min(pc.setpoint.limits)) for pc in sextupoles]
            # ramp_targets = list(itertools.chain(*ramp_targets))
            # ramp kickers back
            ramp_targets = [hk.ps, hk_set, vk.ps, vk_set]
            yield from bps.mv(*ramp_targets)

        else:
            # Just deactivate the kicker
            yield from bps.mv(hk.delay.switch, 1, vk.delay.switch, 1)

    for motor, pos in step.items():
        #pos_c = None
        #if pos_cache is not None:
        pos_c = pos_cache[motor]
        log.debug(f'per step motor {motor.name} pos {pos} pos_cache {pos_c}')

    # log.warning(f'{list(step.keys())}')

    # Not used now ... going out ray per ray

    #if kicker_pos['phi'] !=  last_kicker_pos['phi']:
    #    # new ray ..
    #    yield from bps.mv(dam.finished_ray, 0)
    #    yield from bps.mv(dam.finished, 0)
    #    lifetime.resetCurrentReadings()
    #
    #
    #if kicker_pos['r'] != last_kicker_pos['r']:
    #    yield from bps.mv(dam.finished, 0)
    #    # new pos
    #    lifetime.resetCurrentReadings()

    # i
    yield from bps.move_per_step(step, pos_cache)
    yield from bps.checkpoint()

    motors = step.keys()
    r = yield from bps.trigger_and_read(list(detectors) + list(motors))
    yield from bps.checkpoint()
    #: required for check limits ... no dictonary
    if len(list(r.keys())) == 0:
        return

    current = r[topup_cc.name]['value']
    min_current = .1
    if current < min_current:
        # beam lost
        log.warning(f'Finishing as current {current} < min current {min_current}')
        yield from bps.mv(device.finished, True)
        return
    yield from bps.checkpoint()

    lt_avg_name = lifetime.lt.name
    lt_err_avg_name = lifetime.lt_err.name
    lt_est_avg_name = lifetime.lt_est.name
    lt = r[lt_avg_name]['value']
    if lt < 0.25:
        RE.log.warning(f'Ray scan finished for pos {kicker_pos} lifetime {lt} < 0.25')
        yield from bps.mv(device.finished_ray, True)

     # Seems to destroy data read back
    err_ok = r[lifetime.below_min_err.name]['value']
    est_ok = r[lifetime.above_min_est.name]['value']

    if est_ok or err_ok:
        # That's all folkfs for this setting
        # RE.log.warning(f'Pos scan finished for pos {kicker_pos}')
        yield from bps.mv(device.finished, True)
