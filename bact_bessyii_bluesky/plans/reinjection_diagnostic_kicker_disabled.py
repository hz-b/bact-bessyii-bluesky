import asyncio
import functools

from bluesky import plan_stubs as bps

from bact_bessyii_bluesky.plans.reinjection_plan import reinject_current


def setup_reinjection(
    topup_device, frequency_switcher, horizontal_kicker_device, vertical_kicker_device
):
    """

    Todo:
        find out if plans are already evaluated in async mode
    """
    async def get_kicker_values():
        return await asyncio.gather(
            horizontal_kicker_device.setpoint.get_value(),
            vertical_kicker_device.setpoint.get_value(),
        )

    # hk_reset_value, vk_reset_value = asyncio.get_event_loop().run_until_complete(
    #     get_kicker_values()
    #  )

    def before_injection():
        yield from bps.mv(
            frequency_switcher,
            0.5,
            horizontal_kicker_device,
            0.0,
            vertical_kicker_device,
            0.0,
        )

    def after_injection():
        yield from bps.mv(
            frequency_switcher,
            1.0,
        )
        # yield from bps.mv(
        #    horizontal_kicker_device,
        #    # Todo: shall the kicker value be reset ?
        #    # I guess not
        #    hk_reset_value,
        #    vertical_kicker_device,
        #    vk_reset_value,
        # )

    return functools.partial(
        reinject_current,
        topup_device=topup_device,
        before_injection=before_injection,
        after_injection=after_injection,
    )
