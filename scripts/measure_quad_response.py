import matplotlib
matplotlib.use('QtCairo')
import matplotlib.pyplot as plt
from bact_bessyii_bluesky.applib.bba import measure_quad_response

def main():
    plt.ion()
    try:
        measure_quad_response.main(try_run=True, prefix="Pierre:DT:")
    except:
        raise
    else:
        plt.ioff()
        plt.show()

if __name__ == "__main__":
    main()