"""Plot all data versus index

These plots update on every new data the whole line
"""

import numpy as np
from collections.abc import Sequence
# from bact2.bluesky.hacks.callbacks import LivePlot
from bluesky.callbacks import LivePlot as BlueskyLivePlot


def name_or_root_of_path(txt: str) -> str:
    if '/' in txt:
        return txt.split("/")[0]
    return txt


def bpm_data_to_plot_data(bpm_read):
    return np.array([[bpm_data[plane]['pos_raw'] for plane in ("x", "y")]
            for bpm_data in bpm_read])


class LivePlot(BlueskyLivePlot):
    def event(self, doc):
        "Unpack data from the event and call self.update()."
        # This outer try/except block is needed because multiple event
        # streams will be emitted by the RunEngine and not all event
        # streams will have the keys we want.
        try:
            # This inner try/except block handles seq_num and time, which could
            # be keys in the data or accessing the standard entries in every
            # event.
            try:
                new_x = doc['data'][self.x]
            except KeyError:
                if self.x in ('time', 'seq_num'):
                    new_x = doc[self.x]
                else:
                    raise
            new_y = doc['data'][name_or_root_of_path(self.y)]
        except KeyError:
            # wrong event stream, skip it
            return

        # Special-case 'time' to plot against against experiment epoch, not
        # UNIX epoch.
        if self.x == 'time' and self._epoch == 'run':
            new_x -= self._epoch_offset

        self.update_caches(new_x, new_y)
        self.update_plot()
        super().event(doc)


class PlotLine(LivePlot):

    def doc_to_bpmdata(self, x, y):
        bpm_data = bpm_data_to_plot_data(y)

        if self.y[-1] == "x":
            ya = bpm_data[:, 0]
        elif self.y[-1] == "y":
            ya = bpm_data[:, 1]
        else:
            raise IndexError(f"bpm data plane {self.y[-1]} unknown")

        if isinstance(x, Sequence):
            xa = np.asarray(x)
        else:
            # todo
            # log warning to user (once per run)
            xa = np.arange(len(ya))

        assert(len(xa) == len(ya))
        return xa, ya
    
    def update_caches_top_part(self, x, y):
        """Convert doc to arrays
        """
        return self.doc_to_bpmdata(x, y)

    def update_caches_bottom_part(self, xa, ya):
        """Store arrays compatible to bluesky liveplot expecectations
        well lists to be precices
        """
        self.y_data = ya.tolist()
        self.x_data = xa.tolist()
    
    def update_caches(self, x, y):
        """
        
        Extract line and update cache
        """
        xa, ya = self.update_caches_top_part(x, y)
        self.update_caches_bottom_part(xa, ya)

class Offset:
    def __init__(self):
        self.clearOffset()

    def clearOffset(self):
        self.old_value = None

    def set_ref_value(self, ref):
        self.old_value = np.asarray(ref)
        
    def update_caches(self, x: np.ndarray, y:np.ndarray):
        # Scale to kHz
        if self.old_value is None:
            return x, y
        dy = y - self.old_value
        return x, dy


class PlotLineOffset(PlotLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset = Offset()

    def update_caches(self, x, y):
        xa, ya = self.update_caches_top_part(x, y)
        xa, dya = self.offset.update_caches(xa, ya)
        self.update_caches_bottom_part(xa, dya)
        self.offset.set_ref_value(ya)


class PlotLineVsIndex(LivePlot):
    """plot data versus index
    """

    def update_caches(self, x, y):
        raise NotImplementedError("Code not needed any more")
        ind = np.arange(len(y))
        self.x_data = ind.tolist()
        self.y_data = y.tolist()


class PlotLineVsIndexOffset(PlotLineVsIndex):
    """Plot offset data  versus index

    The first measurement received is used as reference
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset = Offset()

    def update_caches(self, x, y):
        xa, ya = self.update_caches_top_part()
        xa, dya = self.offset.update_caches(xa, ya)
        self.update_caches_bottom_part(xa, dya)
        self.offset.set_ref_value(ya)
