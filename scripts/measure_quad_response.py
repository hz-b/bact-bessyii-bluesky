import matplotlib
matplotlib.use('Qt5Cairo')
# matplotlib.use('Qt')
import matplotlib.pyplot as plt
from bact_bessyii_bluesky.applib.bba import measure_quad_response

def main():
    # prefix = "Pierre:DT:"
    prefix = ""
    currents = [0,2,-2,0]
    currents = [0,.1,-.1,0]
    plt.ion()
    try:
        measure_quad_response.main(prefix=prefix, currents=currents, machine_name="BessyII", catalog_name="heavy_local",measurement_name="beam_based_alignment",try_run=True)
    except:
        raise
    else:
        plt.ioff()
        plt.show()

if __name__ == "__main__":
    main()
