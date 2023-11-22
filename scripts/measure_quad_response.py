import matplotlib
# matplotlib.use('QtCairo')
import matplotlib.pyplot as plt
from bact_bessyii_bluesky.applib.bba import measure_quad_response

def main():
    plt.ion()
    try:
        measure_quad_response.main(prefix="", currents=[0,.5,-.5,0], machine_name="BessyII", catalog_name="heavy_local",measurement_name="beam_based_alignment",try_run=True)
    except:
        raise
    else:
        plt.ioff()
        plt.show()

if __name__ == "__main__":
    main()
