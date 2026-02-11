import bluesky.plan_stubs as bps


def ramp_kicker_voltage_to_target(
        hk_ps, target_horizontal, vk_ps, vertical_target
):
    """Illustrate how to ramp kicker target voltage

    Consider using :func:`bps.mv` directly
    """
    yield from bps.mv(hk_ps, target_horizontal, vk_ps, vertical_target)


def switch_kicker_off(hk_switch, vk_switch):
    """illustrate how to switch kickers off
    """
    yield from bps.mv(hk_switch, 0, vk_switch, 0)
