import click
import geopandas as gpd
import logging
import os
import urllib.request
import subprocess
import shapely
import sys
import zipfile
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

    def __init__(self, source):
        self.stage = 5
        self.source = source.lower()

        # Configure and validate input data path.
        self.data_path = os.path.abspath("../../data/interim/{}.gpkg".format(self.source))
        if not os.path.exists(self.data_path):
            logger.exception("Input data not found: \"{}\".".format(self.data_path))
            sys.exit(1)

    def dl_latest_vintage(self):
        """Downloads the latest provincial NRN dataset.
        For now it is downloading the dataset from STC geoprod rather than locally."""

        # Download latest vintage dataset.
        logger.info("Downloading latest provincial dataset.")
        vintage = "https://geoprod.statcan.gc.ca/nrn_rrn/nb/NRN_RRN_NB_9_0_SHP.zip"
        urllib.request.urlretrieve(vintage, '../../data/raw/vintage.zip')
        with zipfile.ZipFile("../../data/raw/vintage.zip", "r") as zip_ref:
            zip_ref.extractall("../../data/raw/vintage")

        # Transform administrative boundary file to GeoPackage layer with crs EPSG:4617.
        logger.info("Transforming latest provincial dataset.")
        try:
            subprocess.run("ogr2ogr ../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en/NRN_NB_9_0_ROADSEG_tmp.shp "
                           "../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en/NRN_NB_9_0_ROADSEG.shp -t_srs EPSG:4617 "
                           "-lco overwrite=yes ")
        except subprocess.CalledProcessError as e:
            logger.exception("Unable to transform data source to EPSG:4617.")
            logger.exception("ogr2ogr error: {}".format(e))
            sys.exit(1)


    def execute(self):
        """Executes an NRN stage."""

        self.dl_latest_vintage()

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
