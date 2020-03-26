import click
import geopandas as gpd
import logging
import os
import pandas as pd
import urllib.request
import uuid
import subprocess
import sqlite3
import sys
import zipfile
from shapely.ops import split

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
            subprocess.run("ogr2ogr -f \"ESRI Shapefile\" -t_srs EPSG:4617 "
                           "../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en/4617 "
                           "../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en", shell=True)
        except subprocess.CalledProcessError as e:
            logger.exception("Unable to transform data source to EPSG:4617.")
            logger.exception("ogr2ogr error: {}".format(e))
            sys.exit(1)

        logger.info("Reading latest provincial dataset.")
        self.vintage_roadseg = gpd.read_file("../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en/4617/NRN_NB_9_0_ROADSEG.shp")
        # self.vintage_ferryseg = gpd.read_file("../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en/4617/NRN_NB_9_0_FERRYSEG.shp")
        # self.vintage_junction = gpd.read_file("../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en/4617/NRN_NB_9_0_JUNCTION.shp")

    def roadseg_equality(self):
        """Checks if roadseg features have equal geometry."""

        # self.vintage_roadseg = gpd.read_file("../../data/raw/vintage/NRN_RRN_NB_9_0_SHP/NRN_NB_9_0_SHP_en/4617/NRN_NB_9_0_ROADSEG.shp")
        # self.vintage_roadseg = self.dframes["roadseg"]
        self.vintage_roadseg = gpd.read_file("/home/kent/PycharmProjects/nrn-rrn/data/interim/nb.gpkg", layer="roadAOI_old")
        self.dframes["roadseg"] = gpd.read_file("/home/kent/PycharmProjects/nrn-rrn/data/interim/nb.gpkg", layer="roadAOI")

        self.vintage_roadseg_filter = self.vintage_roadseg.filter(items=['geometry', 'nid'])

        # Equal geometry.
        self.equal_geom = pd.merge(self.dframes["roadseg"], self.vintage_roadseg_filter, on="geometry")

        join_out = pd.merge(self.dframes["roadseg"], self.vintage_roadseg_filter, how="outer", indicator=True)

        # Added geometry.
        add_geom = join_out[join_out["_merge"]=="left_only"]

        # Deleted geometry.
        del_geom = join_out[join_out["_merge"] == "right_only"]

        if self.equal_geom is not None:
            for index, row in self.equal_geom.iterrows():
                logger.warning("roadseg: EQUALITY detected for uuid: {}".format(index))
                self.equal_geom["nid_x"] = self.equal_geom["nid_y"]

        if add_geom is not None:
            for index, row in add_geom.iterrows():
                logger.warning("roadseg: ADDITION detected for uuid: {}".format(index))

        if del_geom is not None:
            for index, row in del_geom.iterrows():
                logger.warning("roadseg: DELETION or CHANGE detected for uuid: {}".format(index))

        merged = pd.concat([self.equal_geom, add_geom], sort=True)

        self.merge_add_geom = merged[merged["_merge"]=="left_only"]

        self.merge_add_geom.to_file("/home/kent/PycharmProjects/nrn-rrn/data/interim/add_geom.gpkg", driver="GPKG")
        # sys.exit(1)
        # helpers.export_gpkg({"roadseg2": merged}, self.data_path)

    def split_lines(self):

        juncAOI = gpd.read_file("/home/kent/PycharmProjects/nrn-rrn/data/interim/nb.gpkg", layer="juncAOI")

        # dissolve polygon here

        # subprocess.run("python dissolve.py", shell=True)

        dissolve = gpd.read_file("/home/kent/PycharmProjects/nrn-rrn/data/interim/dissolve.gpkg", driver="GPKG")

        juncAOI = juncAOI.unary_union
        dissolve = dissolve.unary_union

        logger.info("Splitting roadseg with junctions.")
        result = split(dissolve, juncAOI)

        segments = [feature for feature in result]

        add_geom = gpd.GeoDataFrame(list(range(len(segments))), geometry=segments)

        add_geom.columns = ['index', 'geometry']

        add_geom["nid"] = [uuid.uuid4().hex for _ in range(len(add_geom))]

        final = pd.concat([self.equal_geom, add_geom])

        final.to_file("/home/kent/PycharmProjects/nrn-rrn/data/interim/nb.gpkg", driver="GPKG", layer="output")

        sys.exit(1)

    def ferryseg_equality(self):
        """Checks if ferryseg features have equal geometry."""

        logger.info("Checking for ferry segment geometry equality.")
        # Returns True or False to a new column if geometry is equal.
        self.dframes["ferryseg"]["equals"] = self.dframes["ferryseg"].geom_equals(self.vintage_ferryseg)

        logger.info("Logging geometry equality.")
        for index, row in self.dframes["ferryseg"].iterrows():

            if row['equals'] == 1:
                logger.warning("Equal ferryseg geometry detected for uuid: {}".format(index))
                self.dframes["ferryseg"]["nid"] = self.vintage_ferryseg["nid"]

            else:
                logger.warning("Unequal ferryseg geometry detected for uuid: {}".format(index))
                self.dframes["ferryseg"]["nid"] = ""

        logger.info("Writing test ferry segment GPKG.")
        helpers.export_gpkg({"ferryseg_equal": self.dframes["ferryseg"]}, self.data_path)

    def junction_equality(self):
        """Checks if junction features have equal geometry."""

        logger.info("Checking for junction geometry equality.")
        # Returns True or False to a new column if geometry is equal.
        self.dframes["junction"]["equals"] = self.dframes["junction"].geom_equals(self.vintage_junction)

        logger.info("Logging geometry equality.")
        for index, row in self.dframes["junction"].iterrows():

            if row['equals'] == 1:
                logger.warning("Equal junction geometry detected for uuid: {}".format(index))
                self.dframes["junction"]["nid"] = self.vintage_junction["nid"]

            else:
                logger.warning("Unequal junction geometry detected for uuid: {}".format(index))

        logger.info("Writing test junction GPKG.")
        helpers.export_gpkg({"junction_equal": self.dframes["junction"]}, self.data_path)

    def execute(self):
        """Executes an NRN stage."""

        self.load_gpkg()
        # self.dl_latest_vintage()
        self.roadseg_equality()
        self.split_lines()
        self.ferryseg_equality()
        self.junction_equality()

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