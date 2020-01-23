import click
import geopandas as gpd
import glob
import numpy as np
import logging
import os
import urllib.request
import uuid
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

    def load_gpkg(self):
        """Loads input GeoPackage layers into data frames."""

        logger.info("Loading Geopackage layers.")

        self.dframes = helpers.load_gpkg(self.data_path)

    def dl_latest_vintage(self):
        """Downloads the latest provincial NRN data set from Open Maps/FGP."""

        # Download latest vintage data set.
        logger.info("Downloading latest provincial dataset.")
        vintage = "https://geoprod.statcan.gc.ca/nrn_rrn/nb/NRN_RRN_NB_9_0_SHP.zip"
        urllib.request.urlretrieve(vintage, '../../data/raw/vintage.zip')
        with zipfile.ZipFile("../../data/raw/vintage.zip", "r") as zip_ref:
            zip_ref.extractall("../../data/raw/vintage")

        # Transform latest vintage into crs EPSG:4617.
        logger.info("Transforming latest provincial dataset.")
        try:
            subprocess.run('ogr2ogr -f "ESRI Shapefile" -t_srs EPSG:4617 '
                           '../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en/4617 '
                           '../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en')
        except subprocess.CalledProcessError as e:
            logger.exception("Unable to transform data source to EPSG:4617.")
            logger.exception("ogr2ogr error: {}".format(e))
            sys.exit(1)

        logger.info("Reading latest provincial dataset.")
        self.vintage_roadseg = gpd.read_file("../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en/4617/NRN_NB_9_0_ROADSEG.shp")
        self.vintage_ferryseg = gpd.read_file("../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en/4617/NRN_NB_9_0_FERRYSEG.shp")

    def roadseg_equality(self):
        """Checks if roadseg features have equal geometry."""

        # new = self.dframes["roadseg"]
        # print(new)

        # new = gpd.read_file("../../data/interim/nb_test.gpkg", layer="new")
        # new["nid"] = [uuid.uuid4().hex for _ in range(len(new))]
        # old = gpd.read_file("../../data/interim/nb_test.gpkg", layer="old")
        # old["nid"] = [uuid.uuid4().hex for _ in range(len(old))]

        logger.info("Checking for road segment geometry equality.")
        # Returns True or False to a new column if geometry is equal.
        self.dframes["roadseg"]["equals"] = self.dframes["roadseg"].geom_equals(self.vintage_roadseg)

        logger.info("Writing test ROADSEG GPKG.")
        helpers.export_gpkg({"roadseg_equal": self.dframes["roadseg"]}, self.data_path)

    def ferryseg_equality(self):
        """Checks if ferryseg features have equal geometry."""

        logger.info("Checking for ferry segment geometry equality.")
        # Returns True or False to a new column if geometry is equal.
        self.dframes["ferryseg"]["equals"] = self.dframes["ferryseg"].geom_equals(self.vintage_ferryseg)

        logger.info("Writing test FERRYSEG GPKG.")
        helpers.export_gpkg({"ferryseg_equal": self.dframes["ferryseg"]}, self.data_path)

    def execute(self):
        """Executes an NRN stage."""

        self.load_gpkg()
        self.dl_latest_vintage()
        self.roadseg_equality()
        self.ferryseg_equality()

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
