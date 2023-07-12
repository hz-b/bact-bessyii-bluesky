import matplotlib.pyplot as plt
from . import line_index, bpm_plot

def plots(*, magnet_name=None, ds=None, x_pos, y_pos, reading_count=None, **kwargs):
    '''Typical orbit plots

    Plots the measured x and y position on top of the plots

    At the bottom difference is plotted to the orbit that was
    obtained when the magnet name changed.


    Args:
       magnet_name: ophyd device name that contains the
                    magnet name

       ds: ophyd device containing the different positions

       x_pos : x position
       y_pos : y position

    '''
    #--------------------------------------------------
    # Setting up the plots
    # Let"s have the actual x and y positions. Furthermore bpm
    # readings are read more than once. Let's have plots that
    # show how much these readings vary after the first reading
    # is made
    #
    # The figures for x and y ... on top of each other
    fig, axes = plt.subplots(2, 2, figsize=[8,6], sharex=True)
    upper, lower = axes
    ax1, ax2 = upper
    ax3, ax4 = lower
    ax1.grid(True)
    ax2.grid(True)

    'dt_mux_selector_readback'

    line_x = line_index.PlotLine(
        x_pos, x=ds, ax=ax1, legend_keys=['x'], y_scale=kwargs.get("y_scale", 1.0)
    )
    line_y = line_index.PlotLine(
        y_pos, x=ds, ax=ax2, legend_keys=['y'], y_scale=kwargs.get("y_scale", 1.0)
    )

    # xpos = "bpm_waveform_x_pos"
    kwargs = kwargs.copy()
    kwargs.update(dict(x=ds, selected_steerer_name=magnet_name,
                  reading_count=reading_count))
    bpm_x = bpm_plot.BPMOffsetPlot(x_pos, ax=ax3, legend_keys=['dx'], **kwargs)
    bpm_y = bpm_plot.BPMOffsetPlot(y_pos, ax=ax4, legend_keys=['dy'], **kwargs)

    return [line_x, line_y, bpm_x, bpm_y]
