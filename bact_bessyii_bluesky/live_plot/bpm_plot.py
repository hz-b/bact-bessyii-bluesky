"""Plots for comparing the different bpm data

"""

from . import labelled_plot
from . import line_index

# from collections import ChainMap
# import numpy as np
import logging

logger = logging.getLogger("bact2")


class BPMComparisonPlot(labelled_plot.LabelledPlot):
    """

    Todo:
        Investigate if such a plot should be provided for steerers too
    """

    def __init__(self, *args, bpm_names=None, bpm_positions=None, **kwargs):

        assert bpm_names is not None
        assert bpm_positions is not None

        super().__init__(
            *args, label_names=bpm_names, label_positions=bpm_positions, **kwargs
        )


class _BPMPlots(line_index.PlotLineOffset):
    """BPM Plots default to ring position as independent variable
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("x", "bpm_waveform_ds")
        super().__init__(*args, **kwargs)

        try:
            if self.log is None:
                self.log = logger
        except AttributeError:
            self.log = logger


class BPMOrbitOffsetPlot(_BPMPlots):
    """Plot offset to orbit

    As orbit the first measured reference is taken. This is handled by
    :class:`PlotLineVsIndexOffset`
    """


class BPMOffsetPlot(_BPMPlots):
    """Show orbit change dues to steerer settings change

    When the selected steerer name changes the offset is reset

    Args:
        min_count:ignore measurements below this count
        Reading count: name of the counting variable
    """

    def __init__(
        self,
        *args,
        selected_steerer_name=None,
        reading_count=None,
        min_count=1,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if selected_steerer_name is None:
            selected_steerer_name = "sc_selected"

        self.selected_steerer_name = selected_steerer_name
        self.selected_steerer = None

        self.reading_count = reading_count
        self.min_count = min_count

    def ignore_this_reading(self, doc):

        data = doc["data"]
        try:
            cnt = data[self.reading_count]
        except KeyError as ke:
            txt = 'Selected reading count could not be found by name "{}"'
            self.log.error(txt.format(self.reading_count))
            return True

        flag = cnt < self.min_count
        txt = f'"{self.reading_count}: ignore doc {cnt} >= {self.min_count} ? {flag}"'
        self.log.info(txt)
        return flag

    def trace_used_steerer(self, doc):

        # print('bpm offset plot event["data"].keys()= {}'.format(data.keys()))
        # print('selected_sterrer: {}'.format(selected_steerer))

        data = doc["data"]
        try:
            selected_steerer = data[self.selected_steerer_name]
        except KeyError as ke:
            cls_name = self.__class__.__name__
            txt = '{}: Selected magnet could not be found by name "{}"'
            self.log.error(txt.format(cls_name, self.selected_steerer_name))
            self.log.info("available entries %s", list(data.keys()))
            return

        if selected_steerer != self.selected_steerer:
            txt = "Resetting plot as selected steerer switches from {} to {}"
            self.log.warning(txt.format(self.selected_steerer, selected_steerer))
            self.offset.clearOffset()
            self.selected_steerer = selected_steerer

    def event(self, doc):
        if self.ignore_this_reading(doc):
            self.log.debug("Ignoring doc!")
            return

        self.trace_used_steerer(doc)
        return super().event(doc)
