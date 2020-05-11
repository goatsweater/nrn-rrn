"""Definitions for valid layers within the GPKG."""

import logging
import osgeo.ogr as ogr
import pandas as pd
from pathlib import Path
import sqlite3
import tempfile
import zipfile

logger = logging.getLogger(__name__)

def compress(inpath: Path, outfile: Path = None) -> None:
    """Given a directory or file path, create a zip compressed version of it.

    If the outfile path does not contain a .zip extension, one is added.
    """
    # Do not try to compress an existing archive.
    if zipfile.is_zipfile(inpath):
        return None

    # If no output file was provided, use the path of the input file
    if not outfile:
        name = f'{inpath.name}.zip'
        outfile = inpath.parent.joinpath(name)

    # Check if the output is valid
    # TODO: This is a crude check that can still end up creating invalid names.
    if not outfile.name.endswith('.zip'):
        outfile.name = f'{outfile.name}.zip'
    
    # Write all of the contents of the input to the zip archive
    try:
        with zipfile.ZipFile(outfile, 'w') as archive:
            for item in inpath.rglob('*'):
                archive.write(item)
    except (zipfile.BadZipFile, zipfile.LargeZipFile) as err:
        logger.exception("Unable to create zip archive.")
        raise err

def df_to_gpkg(gpkg: Path, df: pandas.DataFrame, table_name: str)
    """Write a non-spatial DataFrame to a GeoPackage file."""
    try:
        # create a connection to the sqlite file
        con = sqlite3.connect(output_path)

        # Write to GeoPackage.
        df.to_sql(table_name, con, if_exists="replace", index=False)

        # Add metedata record to gpkg_contents.
        sql = "INSERT OR IGNORE INTO gpkg_contents (table_name, data_type) VALUES (?,?)"
        con.cursor().execute(sql, (table_name, 'attributes'))
        con.commit()
        con.close()
    except sqlite3.Error as err:
        logger.exception(f"Unable to write to {gpkg}")
        raise err
    



# Base class for layers in a dataset to provide common bits of functionality
class BaseTable:
    """A base class to provide some common functions for all layers.

    This class is not meant to be used directly.
    """
    pass

# Field definitions found in the different tables in each dataset.

class AddressRangeTable(BaseTable):
    """Definition of the address range table."""

    def __init__(self):
        name = 'addrange'
        fields = {
            "acqtech": ogr.FieldDefn("ACQTECH", ogr.OFTString),
            "metacover": ogr.FieldDefn("METACOVER", ogr.OFTString),
            "credate": ogr.FieldDefn("CREDATE", ogr.OFTDate),
            "datasetnam": ogr.FieldDefn("DATASETNAM", ogr.OFTString),
            "accuracy": ogr.FieldDefn("ACCURACY"),
            "provider": ogr.FieldDefn("PROVIDER"),
            "revdate": ogr.FieldDefn("REVDATE", ogr.OFTDate),
            "specvers": ogr.FieldDefn("SPECVERS", ogr.OFTReal),
            "l_altnamnid": ogr.FieldDefn("L_ALTNANID", ogr.OFTString),
            "r_altnamnid": ogr.FieldDefn("R_ALTNANID", ogr.OFTString),
            "l_digdirfg": ogr.FieldDefn("L_DIGDIRFG", ogr.OFTString),
            "r_digdirfg": ogr.FieldDefn("R_DIGDIRFG", ogr.OFTString),
            "l_hnumf": ogr.FieldDefn("L_HNUMF", ogr.OFTString),
            "r_hnumf": ogr.FieldDefn("R_HNUMF", ogr.OFTString),
            "l_hnumsuff": ogr.FieldDefn("L_HNUMSUFF", ogr.OFTString),
            "r_hnumsuff": ogr.FieldDefn("R_HNUMSUFF", ogr.OFTString),
            "l_hnumtypf": ogr.FieldDefn("L_HNUMTYPF", ogr.OFTString),
            "r_hnumtypf": ogr.FieldDefn("R_HNUMTYPF", ogr.OFTString),
            "l_hnumstr": ogr.FieldDefn("L_HNUMSTR", ogr.OFTString),
            "r_hnumstr": ogr.FieldDefn("R_HNUMSTR", ogr.OFTString),
            "l_hnuml": ogr.FieldDefn("L_HNUML", ogr.OFTString),
            "r_hnuml": ogr.FieldDefn("R_HNUML", ogr.OFTString),
            "nid": ogr.FieldDefn("NID", ogr.OFTString),
            "l_hnumsufl": ogr.FieldDefn("L_HNUMSUFL", ogr.OFTString),
            "r_hnumsufl": ogr.FieldDefn("R_HNUMSUFL", ogr.OFTString),
            "l_hnumtypl": ogr.FieldDefn("L_HNUMTYPL", ogr.OFTString),
            "r_hnumtypl": ogr.FieldDefn("R_HNUMTYPL", ogr.OFTString),
            "l_offnanid": ogr.FieldDefn("L_OFFNANID", ogr.OFTString),
            "r_offnanid": ogr.FieldDefn("R_OFFNANID", ogr.OFTString),
            "l_rfsysind": ogr.FieldDefn("L_RFSYSIND", ogr.OFTString),
            "r_rfsysind": ogr.FieldDefn("R_RFSYSIND", ogr.OFTString)
        }
    
    def set_gpkg_name(self, source, major, minor):
        return "NRN_<source>_<major_version>_<minor_version>_ADDRANGE"
    
        

# Common fields
nid_field = ogr.FieldDefn("NID", ogr.OFTString)
datasetnam_field = ogr.FieldDefn("DATASETNAM", ogr.OFTString)
credate_field = ogr.FieldDefn("CREDATE", ogr.OFTDate)
revdate_field = ogr.FieldDefn("REVDATE", ogr.OFTDate)
specvers_field = ogr.FieldDefn("SPECVERS", ogr.OFTReal)
acqtech_field = ogr.FieldDefn("ACQTECH", ogr.OFTString)
