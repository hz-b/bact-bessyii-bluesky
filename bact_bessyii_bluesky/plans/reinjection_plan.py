import logging
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp

from bact_bessyii_ophyd_async.devices.raw.topup_engine import ToppingUpState, Frequency as InjectionFrequency

logger = logging.getLogger("bact-bessyii-bluesky")


def switch_frequency(frequency_switch, target_frequency: InjectionFrequency):
    """Example of switching frequency

    This example only switches frequency and does nothing else

    For BESSY II the standard signal would be
        topup_device.frequency
    """
    yield from bps.mv(frequency_switch, target_frequency)


def reinject_current(topup_device, before_injection, after_injection):
    """
    Todo:
         the user is expected to swich injection frequency if they are
         interested to do so them self.

         Topup engine (device proxy) should be able to delay the switch
         if required
    """
    logger.info('Executing reinjection:  prepare plan finalisation')

    def shutoff_injection_plan():
        logger.info('    finalize plan: switching injection off (anyway)')
        yield from bps.mv(topup_device, ToppingUpState.OFF)
        logger.info('    finalize plan: switching injection off (anyway)')
        logger.info('Executed reinjection')

    @bpp.finalize_decorator(shutoff_injection_plan)
    def inner():
        logger.info('    injection: steps requested for preparation')
        # switching frequency takes a bit of time
        yield from before_injection()
        logger.info('    injection: switching on')
        yield from bps.mv(topup_device, ToppingUpState.ON)
        logger.info('    injected:   switching off')
        yield from bps.mv(topup_device, ToppingUpState.OFF)
        logger.info('    injected:   steps requested for finalising')
        yield from after_injection()
        logger.info('    injected:   finished, handling over to finalise plan')

    logger.info('    injection: calling steps')
    try:
        r = yield from inner()
    except Exception as exc:
        logger.error('    injection  failed: {exc}')
        raise exc
    else:
        logger.info('    injection: finished successfully')
        return r

