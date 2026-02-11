import more_itertools


def produce_in_between(start: float, stop: float, maxdepth: int):
    """Cover the range by ever increasing samller steps...

    Do it
    """
    half = (start + stop) / 2.0
    yield half
    if maxdepth <= 1:
        return
    yield from more_itertools.roundrobin(
        produce_in_between(start, half, maxdepth=maxdepth - 1),
        produce_in_between(half, stop, maxdepth=maxdepth - 1)
    )
