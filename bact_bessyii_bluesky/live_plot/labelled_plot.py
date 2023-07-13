'''Plots with data labels

'''
import logging
from collections import ChainMap
from bluesky.callbacks import LivePlot
import numpy as np

logger = logging.getLogger('bact')


class LabelledPlot(LivePlot):
    '''Liveplot with labels at the x axis

    Provide any variable for the "y" variable. It is currently not
    sensible. Code requires to be fixed.

    Todo:
        fix that not an arbitrary `y` variable needs to be passed
        on
    '''

    def __init__(self, *args, label_names=None, label_positions=None,
                 **kwargs):

        assert(label_names is not None)
        assert(label_positions is not None)

        cls_name = self.__class__.__name__
        logger.debug(
            f'{cls_name}: calling super init with args {args} kwargs {kwargs}'
        )
        super().__init__(*args, **kwargs)

        ln = len(label_names)
        lp = len(label_positions)
        if ln != lp:
            txt = (
                f'Number of label names {ln} does not match the number of '
                f' positions {ln}'
            )
            self.log.error(txt)
            raise AssertionError(txt)

        self._label_names = list(label_names)
        self._label_positions = label_positions
        self._label_names = np.array(self._label_names, dtype='U20')

        self.x_data = None
        self.y_data = None

    def start(self, doc):

        super().start(doc)
        cls_name = self.__class__.__name__
        logger.debug(f'{cls_name}:super.start() finished self.x {self.x}')

        # The doc is not used; we just use the signal that a new run began.
        self._epoch_offset = doc['time']  # used if self.x == 'time'

        self.x_data = self._label_positions
        self.y_data = np.zeros(len(self.x_data), np.float_)
        self.y_data[:] = np.nan

        cls_name = self.__class__.__name__
        print(f'{cls_name} dir(self)')
        label = " :: ".join(
            [str(doc.get(name, name)) for name in self.legend_keys])
        kwargs = ChainMap(self.kwargs, {'label': label})

        self.current_line, = self.ax.plot(self.x_data, self.y_data, **kwargs)
        # self.current_line, = self.ax.plot([], [], **kwargs)
        self.lines.append(self.current_line)

        legend = self.ax.legend(loc=0, title=self.legend_title)
        try:
            # matplotlib v3.x
            self.legend = legend.set_draggable(True)
        except AttributeError:
            # matplotlib v2.x (warns in 3.x)
            self.legend = legend.draggable(True)

        self.setLabelNamesAsXTicks()

    def setLabelNamesAsXTicks(self):
        self.ax.set_xticks(self._label_positions)
        self.ax.set_xticklabels(self._label_names, fontsize='small',
                                verticalalignment='top',
                                horizontalalignment='center')
        for tick in self.ax.get_xticklabels():
            tick.set_rotation(90)

    def update_caches(self, x, y):
        '''
        '''

        lx_d = len(self.x_data)

        if lx_d <= 0:
            cls_name = self.__class__.__name__
            txt = f'{cls_name}: len(self.x_data) = {lx_d} data = {self.x_data}'
            # self.log.error(txt)
            AssertionError(txt)

        cls_name = self.__class__.__name__
        print(f'{cls_name} y value {y}')
        ly = len(y)
        if ly != lx_d:
            fmt = 'Length did not match for len(y) = {} len(self.x_data) = {}'
            txt = fmt.format(ly, lx_d)
            # self.log.error(txt)
            if ly in [0, 1]:
                txt += f' ly = {ly} '
                # self.log.error()
            raise AssertionError(txt)

        self.y_data = y

    def update_plot(self):
        self.current_line.set_data(self.x_data, self.y_data)

        self.ax.relim(visible_only=True)
        self.ax.autoscale_view(tight=True)

        axis = list(self.ax.axis())
        x_data = np.array(self.x_data)
        axis[0] = x_data.min()
        axis[1] = x_data.max()
        self.ax.axis(axis)
        self.ax.figure.canvas.draw_idle()

    def stop(self, doc):
        '''

        Todo:
            Check if stop method can be reworked
        '''
        self.x_data = list(self.x_data)
        self.y_data = list(self.y_data)
        super().stop(doc)
