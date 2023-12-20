import matplotlib
# should be selected by user / account settings
# with qt liveplot works
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from bact_bessyii_bluesky.applib.bba import measure_quad_response
import argparse


def main():
    parser = argparse.ArgumentParser(description="measure matrix orbit response")
    parser.add_argument("--epics-prefix", metavar="prefix", default="Pierre:DT:")
    parser.add_argument("-m", "--magnets-to-process", metavar="magnets", nargs="*")
    parser.add_argument("--catalog-name", metavar="catalog_name", default="heavy_local")
    parser.add_argument("--full-run", default=False, action="store_true")
    args = parser.parse_args()
    plt.ion()
    try:
        measure_quad_response.main(
            prefix=args.epics_prefix,
            currents=[0,2,-2,0],
            machine_name="BessyII",
            catalog_name=args.catalog_name,
            measurement_name="beam_based_alignment",
            magnet_names=args.magnets_to_process,
            try_run=(not args.full_run)
        )
    except:
        raise
    else:
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    main()