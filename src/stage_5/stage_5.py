import click
import geopandas as gpd
import logging
import os
import shapely
import sys
from sqlalchemy import *

sys.path.insert(1, os.path.join(sys.path[0], ".."))
import helpers


# Set logger.
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
logger.addHandler(handler)


class Stage:
    """Defines an NRN stage."""

    """ 
    Conditions of Satisfaction
        - Should compare the geometries of the current data with the previous NRN vintage
        - Should retain NID if there has been no geometry change between vintages 
    """

    def __init__(self, source):
        self.stage = 5
        self.source = source.lower()

        # Configure and validate input data path.
        self.data_path = os.path.abspath("../../data/interim/{}.gpkg".format(self.source))
        if not os.path.exists(self.data_path):
            logger.exception("Input data not found: \"{}\".".format(self.data_path))
            sys.exit(1)

    def equals(self):
        # self.nb_stage_5 = helpers.load_gpkg(self.data_path)
        # print(self.nb_stage_5["roadseg"])

        self.vintage = gpd.read_file("../../data/interim/nb_test.gpkg", layer="vintage")
        self.new = gpd.read_file("../../data/interim/nb_test.gpkg", layer="new")


    def execute(self):
        """Executes an NRN stage."""

        self.equals()

@click.command()
@click.argument("source", type=click.Choice("ab bc mb nb nl ns nt nu on pe qc sk yt parks_canada".split(), False))
def main(source):
    """Executes an NRN stage."""

    try:

        with helpers.Timer():
            stage = Stage(source)
            stage.execute()

    except KeyboardInterrupt:
        logger.exception("KeyboardInterrupt: exiting program.")
        sys.exit(1)


if __name__ == "__main__":
    main()
