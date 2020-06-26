import ast
import click
import fiona
import geopandas as gpd
import json
import logging
import numpy as np
import os
import pandas as pd
import re
import requests
import shutil
import sys
import uuid
import zipfile
from collections import Counter
from datetime import datetime
from operator import itemgetter
from shapely.wkt import loads

sys.path.insert(1, os.path.join(sys.path[0], ".."))
import field_map_functions
import helpers


# Suppress pandas chained assignment warning.
pd.options.mode.chained_assignment = None


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
        self.stage = 1
        self.source = source.lower()

        # Configure raw data path.
        self.data_path = os.path.abspath("../../data/raw/{}".format(self.source))

        # Configure source attribute path.
        self.source_attribute_path = os.path.abspath("sources/{}".format(self.source))

        # Validate output namespace.
        self.output_path = os.path.join(os.path.abspath("../../data/interim"), "{}.gpkg".format(self.source))
        if os.path.exists(self.output_path):
            logger.exception("Output namespace already occupied: \"{}\".".format(self.output_path))
            sys.exit(1)

        # Configure field defaults, dtypes, and domains.
        self.defaults = helpers.compile_default_values()
        self.dtypes = helpers.compile_dtypes()
        self.domains = helpers.compile_domains()

    def apply_domains(self):
        """Applies domain restrictions to each column in the target dataframes."""

        logging.info("Applying field domains.")
        table = None
        field = None

        try:

            for table in self.target_gdframes:
                for field, domain in self.domains[table].items():

                    logger.info(f"Applying domain to table: {table}, field: {field}.")

                    # Copy series as object dtype.
                    series_orig = self.target_gdframes[table][field].copy(deep=True).astype(object)

                    # Apply domain to series.
                    series_new = helpers.apply_domain(series_orig, domain=domain["lookup"],
                                                      default=self.defaults[table][field])

                    # Force adjust data type.
                    series_new = series_new.astype(self.dtypes[table][field])

                    # Store results to target dataframe.
                    self.target_gdframes[table][field] = series_new.copy(deep=True)

                    # Compile and log modifications.
                    mods = series_orig.astype(str) != series_new.astype(str)
                    if mods.any():

                        # Compile and quantify modifications.
                        df = pd.DataFrame({"orig": series_orig[mods], "new": series_new[mods]})
                        counts = Counter(series_orig[mods].fillna(-99))

                        # Iterate and log record modifications.
                        for vals in df[~df.duplicated(keep="first")].values:

                            logger.warning(f"Modified {counts[-99] if pd.isna(vals[0]) else counts[vals[0]]} "
                                           f"instance(s) of {vals[0]} to {vals[1]}.")

        except (AttributeError, KeyError, ValueError):
            logger.exception(f"Invalid schema definition for table: {table}, field: {field}.")
            sys.exit(1)

    def apply_field_mapping(self):
        """Maps the source dataframes to the target dataframes via user-specific field mapping functions."""

        logger.info("Applying field mapping.")

        # Retrieve source attributes and dataframe.
        for source_name, source_attributes in self.source_attributes.items():
            source_gdf = self.source_gdframes[source_name]

            # Retrieve target attributes.
            for target_name in source_attributes["conform"]:
                logger.info("Applying field mapping from {} to {}.".format(source_name, target_name))

                # Retrieve table field mapping attributes.
                maps = source_attributes["conform"][target_name]

                # Field mapping.
                for target_field, source_field in maps.items():

                    # Retrieve target dataframe.
                    target_gdf = self.target_gdframes[target_name]

                    # No mapping.
                    if source_field is None:
                        logger.info("Target field \"{}\": No mapping provided.".format(target_field))

                    # Raw value mapping.
                    elif isinstance(source_field, str) and (source_field.lower() not in source_gdf.columns):
                        logger.info("Target field \"{}\": Applying raw value field mapping.".format(target_field))

                        # Update target dataframe with raw value.
                        target_gdf[target_field] = source_field

                    # Function mapping.
                    else:
                        logger.info("Target field \"{}\": Identifying function chain.".format(target_field))

                        # Restructure dict for direct field mapping in case of string or list input.
                        if isinstance(source_field, str) or isinstance(source_field, list):
                            source_field = {"fields": [source_field] if isinstance(source_field, str) else source_field,
                                            "functions": [{"function": "direct"}]}

                        # Convert single field attribute to list.
                        if isinstance(source_field["fields"], str):
                            source_field["fields"] = [source_field["fields"]]

                        # Convert field to lowercase.
                        source_field["fields"] = list(map(str.lower, source_field["fields"]))

                        # Create mapped dataframe from source and target dataframes, keeping only the source fields.
                        mapped_df = pd.DataFrame({field: target_gdf["uuid"].map(
                            source_gdf.set_index("uuid", drop=False)[field]) for field in source_field["fields"]})

                        # Determine if source fields must be processed separately or together.
                        try:
                            process_separately = itemgetter("process_separately")(source_field)
                        except KeyError:
                            process_separately = False

                        # Create dataframe to hold results if multiple fields are given and not processed separately.
                        if not process_separately or len(source_field["fields"]) == 1:
                            results = pd.Series()
                        else:
                            results = pd.DataFrame(columns=range(len(source_field["fields"])))

                        # Iterate source fields.
                        for index, field in enumerate(source_field["fields"]):

                            # Retrieve series from mapped dataframe.
                            if process_separately or len(source_field["fields"]) == 1:
                                mapped_series = mapped_df[field]
                            else:
                                mapped_series = mapped_df.apply(lambda row: row.values, axis=1)

                            # Apply field mapping functions to mapped series.
                            field_mapping_results = self.apply_functions(mapped_series, source_field["functions"])

                            # Store results.
                            if isinstance(results, pd.Series):
                                results = field_mapping_results.copy(deep=True)
                                break
                            else:
                                results[index] = field_mapping_results.copy(deep=True)

                        # Convert results dataframe to series, if required.
                        if isinstance(results, pd.Series):
                            field_mapping_results = results.copy(deep=True)
                        else:
                            field_mapping_results = results.apply(lambda row: row.values, axis=1)

                        # Update target dataframe.
                        target_gdf[target_field] = field_mapping_results.copy(deep=True)

                    # Store updated target dataframe.
                    self.target_gdframes[target_name] = target_gdf.copy(deep=True)

    def apply_functions(self, series, func_list):
        """Iterates and applies field mapping function(s) to a pandas series."""

        # Iterate functions.
        for func in func_list:
            func_name = func["function"]
            params = {k: v for k, v in func.items() if k != "function"}

            logger.info("Applying field mapping function: {}.".format(func_name))

            # Generate expression.
            expr = "field_map_functions.{}(\"val\", **{})".format(func_name, params)

            try:

                # Sanitize expression.
                parsed = ast.parse(expr, mode="eval")
                fixed = ast.fix_missing_locations(parsed)
                compile(fixed, "<string>", "eval")

                # Execute expression.
                if func_name == "direct":
                    series = field_map_functions.direct(series, **params)
                else:
                    series = eval(f"field_map_functions.{func_name}(series, **params)").copy(deep=True)

            except (SyntaxError, ValueError):
                logger.exception("Invalid expression: \"{}\".".format(expr))
                sys.exit(1)

        return series

    def clean_datasets(self):
        """Applies a series of data cleanups to certain datasets."""

        logger.info(f"Applying data cleanup functions.")

        def lower_case_ids(table, df):
            """Sets all ID fields to lower case."""

            logger.info(f"Applying data cleanup \"lower case IDs\" to dataset: {table}.")

            # Iterate columns which a) end with "id", b) are str type, and c) are not uuid.
            dtypes = self.dtypes[table]
            for col in [fld for fld in df.columns.difference(["uuid"]) if fld.endswith("id") and dtypes[fld] == "str"]:

                # Filter records to non-default values which are not already lower case.
                default = self.defaults[table][col]
                s_filtered = df[df[col].map(lambda val: val != default and not val.islower())][col]

                # Apply modifications, if required.
                if len(s_filtered):
                    df.loc[s_filtered.index, col] = s_filtered.map(str.lower)

                    # Quantify and log modifications.
                    logger.warning(f"Modified {len(s_filtered)} record(s) in table {table}, column {col}."
                                   "\nModification details: Column values set to lower case.")

            return df.copy(deep=True)

        def overwrite_roadsegid(series):
            """Populates the series with incrementing integer values from 1-n."""

            logger.info(f"Applying data cleanup \"overwrite roadsegid\" to dataset: roadseg.")

            return pd.Series(range(1, len(series) + 1), index=series.index)

        def strip_whitespace(table, df):
            """Strips leading, trailing, and multiple internal whitespace for each dataframe column."""

            logger.info(f"Applying data cleanup \"strip whitespace\" to dataset: {table}.")

            # Compile valid columns.
            cols = df.select_dtypes(include="object", exclude="geometry").columns.values

            # Iterate columns.
            for col in cols:

                # Apply modifications.
                series_orig = df[col]
                df[col] = df[col].map(lambda val: re.sub(r" +", " ", str(val.strip())))

                # Quantify and log modifications.
                mods = (series_orig != df[col]).sum()
                if mods:
                    logger.warning(f"Modified {mods} record(s) in table {table}, column {col}."
                                   "\nModification details: Column values stripped of leading, trailing, and multiple "
                                   "internal whitespace.")

            return df.copy(deep=True)

        def title_case_route_names(table, df):
            """
            Sets to title case all route name attributes:
                rtename1en, rtename2en, rtename3en, rtename4en,
                rtename1fr, rtename2fr, rtename3fr, rtename4fr.
            """

            logger.info(f"Applying data cleanup \"title case route names\" to dataset: {table}.")

            # Identify columns to iterate.
            cols = [col for col in ("rtename1en", "rtename2en", "rtename3en", "rtename4en",
                                    "rtename1fr", "rtename2fr", "rtename3fr", "rtename4fr") if col in df.columns]

            # Iterate columns.
            for col in cols:

                # Filter records to non-default values which are not already title case.
                default = self.defaults[table][col]
                s_filtered = df[df[col].map(lambda route: route != default and not route.istitle())][col]

                # Apply modifications, if required.
                if len(s_filtered):
                    df.loc[s_filtered.index, col] = s_filtered.map(str.title)

                    # Quantify and log modifications.
                    logger.warning(f"Modified {len(s_filtered)} record(s) in table {table}, column {col}."
                                   "\nModification details: Column values set to title case.")

            return df.copy(deep=True)

        # Cleanup: lower case IDs.
        for table, df in self.target_gdframes.items():
            self.target_gdframes.update({table: lower_case_ids(table, df.copy(deep=True))})

        # Cleanup: overwrite roadsegid.
        roadsegid = self.target_gdframes["roadseg"]["roadsegid"].copy(deep=True)
        self.target_gdframes["roadseg"].loc[roadsegid.index, "roadsegid"] = overwrite_roadsegid(roadsegid)

        # Cleanup: strip whitespace.
        for table, df in self.target_gdframes.items():
            self.target_gdframes.update({table: strip_whitespace(table, df.copy(deep=True))})

        # Cleanup: title case route text.
        for table in ("ferryseg", "roadseg"):
            df = self.target_gdframes[table].copy(deep=True)
            self.target_gdframes.update({table: title_case_route_names(table, df)})

    def compile_source_attributes(self):
        """Compiles the yaml files in the sources' directory into a dictionary."""

        logger.info("Identifying source attribute files.")
        files = [os.path.join(self.source_attribute_path, f) for f in os.listdir(self.source_attribute_path) if
                 f.endswith(".yaml")]

        logger.info("Compiling source attribute yamls.")
        self.source_attributes = dict()

        for f in files:
            # Load yaml and store contents.
            self.source_attributes[os.path.splitext(os.path.basename(f))[0]] = helpers.load_yaml(f)

    def compile_target_attributes(self):
        """Compiles the target (distribution format) yaml file into a dictionary."""

        logger.info("Compiling target attribute yaml.")
        table = field = None

        # Load yaml.
        self.target_attributes = helpers.load_yaml(os.path.abspath("../distribution_format.yaml"))

        # Remove field length from dtype attribute.
        logger.info("Configuring target attributes.")
        try:

            for table in self.target_attributes:
                for field, vals in self.target_attributes[table]["fields"].items():
                    self.target_attributes[table]["fields"][field] = vals[0]

        except (AttributeError, KeyError, ValueError):
            logger.exception("Invalid schema definition for table: {}, field: {}.".format(table, field))
            sys.exit(1)

    def download_previous_vintage(self):
        """
        1) Downloads the previous NRN vintage.
        2) Standardizes table and field names to match interim data format (instead of exported format).
        3) Exports previous NRN vintage as <source>_old.gpkg.
        """

        logger.info("Retrieving previous NRN vintage.")
        source = helpers.load_yaml("../downloads.yaml")["previous_nrn_vintage"]

        # Retrieve metadata for previous NRN vintage.
        logger.info("Retrieving metadata for previous NRN vintage.")
        metadata_url = source["metadata_url"].replace("<id>", source["ids"][self.source])

        # Get metadata from url.
        metadata = helpers.get_url(metadata_url, timeout=30)

        # Extract download url from metadata.
        metadata = json.loads(metadata.content)
        download_url = metadata["result"]["resources"][0]["url"]

        # Download previous NRN vintage.
        logger.info("Downloading previous NRN vintage.")

        try:

            # Get raw content stream from download url.
            download = helpers.get_url(download_url, stream=True, timeout=30)

            # Copy download content to file.
            with open("../../data/interim/nrn_old.zip", "wb") as f:
                shutil.copyfileobj(download.raw, f)

        except (requests.exceptions.RequestException, shutil.Error) as e:
            logger.exception("Unable to download previous NRN vintage: \"{}\".".format(download_url))
            logger.exception(e)
            sys.exit(1)

        # Extract zipped data.
        logger.info("Extracting zipped data for previous NRN vintage.")

        gpkg_path = [f for f in zipfile.ZipFile("../../data/interim/nrn_old.zip", "r").namelist() if
                     f.endswith(".gpkg")][0]

        with zipfile.ZipFile("../../data/interim/nrn_old.zip", "r") as zip_f:
            with zip_f.open(gpkg_path) as zsrc, open("../../data/interim/nrn_old.gpkg", "wb") as zdest:
                shutil.copyfileobj(zsrc, zdest)

        # Load previous NRN vintage into dataframes.
        logger.info("Loading previous NRN vintage into dataframes.")

        self.dframes_old = helpers.load_gpkg("../../data/interim/nrn_old.gpkg", find=True)

        # Standardize table and field names.
        logger.info("Standardizing previous NRN vintage to match interim format.")

        for name, dframe in self.dframes_old.items():
            dframe.columns = map(str.lower, dframe.columns)
            self.dframes_old[name] = dframe.copy(deep=True)

        # Export standardized previous NRN vintage for usage in later stages.
        logger.info("Exporting previous NRN vintage dataframes to GeoPackage layers.")
        helpers.export_gpkg(self.dframes_old, "../../data/interim/{}_old.gpkg".format(self.source))

        # Remove temporary files.
        logger.info("Removing temporary previous NRN vintage files and directories.")
        for f in os.listdir("../../data/interim"):
            if os.path.splitext(f)[0] == "nrn_old":
                path = os.path.join("../../data/interim", f)
                try:
                    os.remove(path) if os.path.isfile(path) else shutil.rmtree(path)
                except (OSError, shutil.Error) as e:
                    logger.warning("Unable to remove directory or file: \"{}\".".format(os.path.abspath(path)))
                    logger.warning(e)
                    continue

    def export_gpkg(self):
        """Exports the target dataframes as GeoPackage layers."""

        logger.info("Exporting target dataframes to GeoPackage layers.")

        # Export target dataframes to GeoPackage layers.
        helpers.export_gpkg(self.target_gdframes, self.output_path)

    def filter_and_relink_strplaname(self):
        """
        For strplaname:
        1) Filter duplicate records.
        2) Repair nid linkages.
        """

        df = self.target_gdframes["strplaname"].copy(deep=True)

        # Filter duplicates.
        logger.info("Filtering duplicates from strplaname.")

        # Define match fields and drop duplicates.
        match_fields = list(df.columns.difference(["uuid", "nid"]))
        df_new = df.drop_duplicates(subset=match_fields, keep="first", inplace=False)

        if len(df) != len(df_new):

            # Store results.
            self.target_gdframes["strplaname"] = df_new.copy(deep=True)

            # Quantify removed duplicates.
            logger.info(f"Dropped {len(df) - len(df_new)} duplicated records from strplaname.")

            # Repair nid linkages.
            logger.info("Repairing strplaname.nid linkages.")

            # Define nid linkages.
            linkages = {
                "addrange": ["l_offnanid", "r_offnanid"],
                "altnamlink": ["strnamenid"]
            }

            # Generate nid lookup dict.
            # Process: group nids by match fields, set first value in each group as index, explode groups, create dict
            # from reversed index and values.
            nids_grouped = helpers.groupby_to_list(df, match_fields, "nid")
            nids_grouped.index = nids_grouped.map(itemgetter(0))
            nids_exploded = nids_grouped.explode()
            nid_lookup = dict(zip(nids_exploded.values, nids_exploded.index))

            # Iterate nid linkages.
            for table in set(linkages).intersection(set(self.target_gdframes)):
                for field in linkages[table]:

                    # Repair nid linkage.
                    series = self.target_gdframes[table][field].copy(deep=True)
                    self.target_gdframes[table].loc[series.index, field] = series.map(
                        lambda val: itemgetter(val)(nid_lookup))

                    # Quantify and log modifications.
                    mods_count = (series != self.target_gdframes[table][field]).sum()
                    if mods_count:
                        logger.warning(f"Repaired {mods_count} linkage(s) between strplaname.nid - {table}.{field}.")

    def gen_source_dataframes(self):
        """Loads input data into a geopandas dataframe."""

        logger.info("Loading input data as dataframes.")
        self.source_gdframes = dict()

        for source, source_yaml in self.source_attributes.items():

            logger.info("Loading data source {}, layer={}.".format(source_yaml["data"]["filename"],
                                                                   source_yaml["data"]["layer"]))

            # Configure filename absolute path.
            source_yaml["data"]["filename"] = os.path.join(self.data_path, source_yaml["data"]["filename"])

            # Spatial.
            if source_yaml["data"]["spatial"]:
                kwargs = {"filename": os.path.abspath("../../data/interim/{}_temp.geojson".format(self.source))}

                # Transform data source crs.
                logger.info("Transforming data source to EPSG:4617 and rounding coordinates to 7 decimal places.")

                nlt = "Point" if {"ferryseg", "roadseg"}.isdisjoint(set(source_yaml["conform"])) else "LineString"

                helpers.ogr2ogr({
                    "overwrite": "-overwrite",
                    "where": f"-where \"{source_yaml['data']['query']}\"" if source_yaml["data"]["query"] else "",
                    "t_srs": "-t_srs EPSG:4617",
                    "s_srs": f"-s_srs {source_yaml['data']['crs']}",
                    "dest": f"\"{kwargs['filename']}\"",
                    "src": f"\"{source_yaml['data']['filename']}\"",
                    "src_layer": source_yaml["data"]["layer"] if source_yaml["data"]["layer"] else "",
                    "lco": "-lco coordinate_precision=7",
                    "nlt": f"-nlt {nlt}"
                })

            # Tabular.
            else:
                kwargs = source_yaml["data"]

            # Load source into dataframe.
            logger.info("Loading data source as (Geo)DataFrame.")
            try:
                gdf = gpd.read_file(**kwargs)
            except fiona.errors.FionaValueError:
                logger.exception("ValueError raised when importing source {}.".format(kwargs["filename"]))
                sys.exit(1)

            # Remove temp data source.
            logger.info("Removing temporary data source output.")
            try:
                os.remove(kwargs["filename"])
            except OSError as e:
                logger.warning("Unable to remove file: \"{}\".".format(kwargs["filename"]))
                logger.warning(e)

            # Force lowercase field names.
            gdf.columns = map(str.lower, gdf.columns)

            # Add uuid field.
            gdf["uuid"] = [uuid.uuid4().hex for _ in range(len(gdf))]

            # Store result.
            self.source_gdframes[source] = gdf
            logger.info("Successfully loaded dataframe.")

    def gen_target_dataframes(self):
        """Creates empty dataframes for all applicable output tables based on the input data field mapping."""

        logger.info("Creating target dataframes for applicable tables.")
        self.target_gdframes = dict()

        # Retrieve target table names from source attributes.
        for source, source_yaml in self.source_attributes.items():
            for table in source_yaml["conform"]:

                logger.info("Creating target dataframe: {}.".format(table))

                # Spatial.
                if self.target_attributes[table]["spatial"]:

                    # Generate target dataframe from source uuid and geometry fields.
                    gdf = gpd.GeoDataFrame(self.source_gdframes[source][["uuid"]],
                                           geometry=self.source_gdframes[source].geometry)

                # Tabular.
                else:

                    # Generate target dataframe from source uuid field.
                    gdf = pd.DataFrame(self.source_gdframes[source][["uuid"]])

                # Add target field schema.
                gdf = gdf.assign(**{field: pd.Series(dtype=dtype) for field, dtype in
                                    self.target_attributes[table]["fields"].items()})

                # Store result.
                self.target_gdframes[table] = gdf
                logger.info("Successfully created target dataframe: {}.".format(table))

        # Log unavailable datasets.
        for table in [t for t in self.target_attributes if t not in self.target_gdframes]:

            logger.warning("Source data provides no field mappings for table: {}.".format(table))

    def recover_missing_datasets(self):
        """
        Recovers missing NRN datasets in the current vintage from the previous vintage.
        Exception: junction.
        """

        # Identify datasets to be recovered.
        recovery_tables = [t for t in self.target_attributes if t not in self.target_gdframes and t != "junction"]
        if any(recovery_tables):

            logger.info("Recovering missing datasets from the previous NRN vintage.")

            # Iterate recovery datasets.
            for table in recovery_tables:

                # Recover dataset if available and not empty.
                if table in self.dframes_old and len(self.dframes_old[table]):

                        logger.info("Recovering dataset: {}.".format(table))

                        df = self.dframes_old[table].copy(deep=True)

                        # Add uuid field.
                        df["uuid"] = [uuid.uuid4().hex for _ in range(len(df))]

                        # Round coordinates to decimal precision = 7.
                        df["geometry"] = df["geometry"].map(
                            lambda g: loads(re.sub(r"\d*\.\d+", lambda m: "{:.7f}".format(float(m.group(0))), g.wkt)))

                        # Store result.
                        self.target_gdframes[table] = df.copy(deep=True)

                # Log unrecoverable dataset.
                else:

                    logger.info("Previous NRN vintage has no recoverable dataset: {}.".format(table))

    def split_strplaname(self):
        """
        For strplaname:
        1) Duplicates all records in strplaname if at least one nested column exists. The first instance will have the
           first nested value, the second instance will have the second nested value.
        2) Repairs nid linkages for right-side records.

        This process creates the left- and right-side representation which strplaname is supposed to possess.
        """

        logger.info("Splitting strplaname to create left- and right-side representation.")

        # Compile nested column names.
        sample_value = self.target_gdframes["strplaname"].iloc[0]
        nested_flags = list(map(lambda val: isinstance(val, np.ndarray) or isinstance(val, list), sample_value))
        cols = sample_value.index[nested_flags].to_list()

        if len(cols):

            # Duplicate dataframe as left- and right-side representations.
            df_l = self.target_gdframes["strplaname"].copy(deep=True)
            df_r = self.target_gdframes["strplaname"].copy(deep=True)

            # Iterate nested columns and keep the 1st and 2nd values for left and right dataframes, respectively.
            for col in cols:
                df_l.loc[df_l.index, col] = df_l[col].map(itemgetter(0))
                df_r.loc[df_r.index, col] = df_r[col].map(itemgetter(1))

            # Generate new nids, uuids, and indexes for right dataframe.
            df_r["nid"] = [uuid.uuid4().hex for _ in range(len(df_r))]
            df_r["uuid"] = [uuid.uuid4().hex for _ in range(len(df_r))]
            df_r.index = df_r["uuid"]

            # Update target dataframe.
            self.target_gdframes["strplaname"] = pd.concat([df_l, df_r], ignore_index=False).copy(deep=True)

            # Generate lookup dict between old and new nids for right dataframe.
            nid_lookup = dict(zip(df_l["nid"], df_r["nid"]))

            # Repair nid linkages.
            logger.info("Repairing strplaname.nid linkages.")

            # Define nid linkages.
            linkages = {
                "addrange": ["r_offnanid"]
            }

            # Iterate nid linkages.
            for table in set(linkages).intersection(set(self.target_gdframes)):
                for field in linkages[table]:

                    # Repair nid linkage.
                    series = self.target_gdframes[table][field].copy(deep=True)
                    self.target_gdframes[table].loc[series.index, field] = series.map(
                        lambda val: itemgetter(val)(nid_lookup))

                    # Quantify and log modifications.
                    mods_count = (series != self.target_gdframes[table][field]).sum()
                    if mods_count:
                        logger.warning(f"Repaired {mods_count} linkage(s) between strplaname.nid - {table}.{field}.")

            # Update altnamlink.
            if "altnamlink" in self.target_gdframes:

                logger.info("Updating altnamlink.")

                # Duplicate records.
                df_first = self.target_gdframes["altnamlink"].copy(deep=True)
                df_second = self.target_gdframes["altnamlink"].copy(deep=True)

                # Generate new strnamenids, uuids, and indexes for second dataframe.
                df_second["strnamenid"] = [uuid.uuid4().hex for _ in range(len(df_second))]
                df_second["uuid"] = [uuid.uuid4().hex for _ in range(len(df_second))]
                df_second.index = df_second["uuid"]

                # Update columns, if required.
                df_second["credate"] = datetime.today().strftime("%Y%m%d")
                df_second["revdate"] = self.defaults["altnamlink"]["revdate"]
                df_second["strnamenid"] = df_second["strnamenid"].map(lambda val: itemgetter(nid_lookup)(val))

                # Store results.
                self.target_gdframes["altnamlink"] = pd.concat([df_first, df_second],
                                                               ignore_index=False).copy(deep=True)

    def execute(self):
        """Executes an NRN stage."""

        self.download_previous_vintage()
        self.compile_source_attributes()
        self.compile_target_attributes()
        self.gen_source_dataframes()
        self.gen_target_dataframes()
        self.apply_field_mapping()
        self.split_strplaname()
        self.recover_missing_datasets()
        self.apply_domains()
        self.clean_datasets()
        self.filter_and_relink_strplaname()
        self.export_gpkg()


@click.command()
@click.argument("source", type=click.Choice("ab bc mb nb nl ns nt nu on pe qc sk yt".split(), False))
def main(source):
    """Executes an NRN stage."""

    try:

        with helpers.Timer():
            stage = Stage(source)
            stage.execute()

    except KeyboardInterrupt:
        logger.exception("KeyboardInterrupt: Exiting program.")
        sys.exit(1)

if __name__ == "__main__":
    main()
