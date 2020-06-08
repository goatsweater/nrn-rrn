"""Processes related to building junctions."""

import datetime
import geobasenrn as nrn
import geopandas as gpd
import logging
import networkx as nx
import pandas as pd
from pathlib import Path
from shapely.geometry import shape, Point

logger = logging.getLogger(__name__)

def get_statcan_admin_boundary_poly(source_prov: str, boundary_file_path: Path):
    """Extract the administrative boundary for the given province or territory."""
    # StatCan uses codes instead of ISO identifiers for the area identifiers
    prov_codes = {"ab": 48, "bc": 59, "mb": 46, "nb": 13, "nl": 10, "ns": 12, "nt": 61, "nu": 62, "on": 35, "pe": 11,
                 "qc": 24, "sk": 47, "yt": 60}
    
    if source_prov not in prov_codes:
        raise ValueError("Invalid province code. Only two letter ISO codes are supported.")
    if not isinstance(boundary_file_path, Path):
        raise ValueError("Boundary file path is not a valid path.")
    
    # Read the administrative boundaries file and filter it
    prov_code = str(prov_codes[source_prov.lower()])
    logger.debug("Filtering boundaries to PRUID == %s", prov_code)
    boundaries = (gpd.read_file(boundary_file_path)
                  .to_crs(nrn.SRS_EPSG_CODE)
                  .rename(columns=str.lower))
    boundaries = boundaries[boundaries['pruid'] == prov_code]
    logger.debug("Number of boundaries found: %d", len(boundaries))
    # There should be only one boundary left - take the geometry
    boundary_geom = boundaries.geometry.to_list()[0]

    return boundary_geom

def _get_start_and_end_points(geo_df):
    """Extract all the start and end points for the GeoDataFrame."""
    logger.debug("Finding all start points for given GeoDataFrame")
    start_points = gpd.GeoSeries(geo_df.geometry.apply(lambda geom: Point(geom.coords[0])))
    logger.debug("Finding all end points for given GeoDataFrame")
    end_points = gpd.GeoSeries(geo_df.geometry.apply(lambda geom: Point(geom.coords[-1])))

    # Concatenate all the points into one large series
    logger.debug("Combining start and end points")
    all_points = pd.concat([start_points, end_points]).to_frame().rename(columns={0: 'geom'}).set_geometry('geom')

    logger.debug("Getting WKB for all points")
    all_points['wkb'] = all_points.geometry.apply(lambda geom: geom.wkb)

    logger.debug("Removing duplicates")
    all_points = all_points.drop_duplicates(subset='wkb')

    logger.debug("Unique points identified")
    return all_points

def build_junctions(road_df, admin_boundary_poly, ferry_df = gpd.GeoDataFrame()):
    """Find all the junction points in the linear datasets and classify them according to NRN rules."""
    logger.debug("Calculating junctions")

    # Column name to set for the junction type
    type_field_name = 'junctype'
    # Collect all the intersections into a list to be combined later
    all_junctions = []
    # Gather all the start and end points into a list for later
    all_start_end_points = []

    # Look for road junctions first
    road_juncs = get_road_intersections(road_df, type_field_name)
    # Save the data out for reference later
    all_junctions.append(road_juncs)
    all_start_end_points.append(_get_start_and_end_points(road_df))

    # Now look for ferry junctions, if ferry routes are provided
    if not ferry_df.empty:
        logger.debug("Getting ferry junctions")
        ferry_juncs = gpd.overlay(road_df, ferry_df, how='intersection', keep_geom_type=False)
        ferry_juncs[type_field_name] = 'Ferry'
        # Drop all the extra columns
        ferry_juncs = ferry_juncs.filter(['geometry', type_field_name])
        # Save the data out for reference later
        all_junctions.append(ferry_juncs)
        all_start_end_points.append(_get_start_and_end_points(ferry_df))

    # Dead-ends are the end of a line that does not intersect with anything else
    logger.debug("Finding dead-ends")
    dead_ends = pd.concat(all_start_end_points)
    dead_ends = dead_ends.set_geometry('geom')
    dead_ends[type_field_name] = 'DeadEnd'
    
    # Remove already found road and ferry junctions
    logger.debug("Removing junctions already found in roads")
    dead_ends = gpd.overlay(dead_ends, road_juncs, how='symmetric_difference', keep_geom_type=False)
    if not ferry_df.empty:
        logger.debug("Removing junctions already found in ferrys")
        dead_ends = gpd.overlay(dead_ends, ferry_juncs, how='symmetric_difference', keep_geom_type=False)

    # Dead-ends outside the administrative boundary are classed as NatProvTer since they connect to a neighbour dataset
    logger.debug("Getting junctions at administrative boundaries")
    dead_ends.loc[~dead_ends.geometry.within(admin_boundary_poly), type_field_name] = 'NatProvTer'
    # Save the data out for reference later
    all_junctions.append(dead_ends)

    logger.debug("Calculating junction attributes")
    junctions = pd.concat(all_junctions)
    junctions["acqtech"] = "Computed"
    junctions["metacover"] = "Complete"
    junctions["specvers"] = nrn.__spec_version__
    junctions["credate"] = datetime.datetime.today().strftime("%Y%m%d")
    junctions["provider"] = "Federal"

    # Retrive a given attribute from associated edges
    net_graph = get_graph_for_lines(road_df)
    for copy_attr_field in ('exitnbr', 'accuracy'):
        logger.debug("Looking for %s values across %d records", copy_attr_field, len(junctions))
        junctions[copy_attr_field] = junctions.geometry.apply(lambda geom: get_attribute_for_node(net_graph, 
                                                                                                geom.coords[0], 
                                                                                                copy_attr_field))

    return junctions

def get_road_intersections(df: gpd.GeoDataFrame, type_field_name: str, junction_min_point_count: int=3):
    """Extract intersections where three or more lines meet in a GeoDataFrame of linear features."""
    logger.debug("Gathering intersections")
    intersection = gpd.overlay(df, df, how='intersection', keep_geom_type=False)
    # Self intersections will create more than just points, but only the points are of interest
    intersection = intersection[intersection.geometry.type == 'Point']

    # There needs to be three or more points at an intersection.
    logger.debug("Calculating shape WKB")
    # You can't groupby on a geometry, so use the WKB representation
    intersection['wkb'] = intersection.geometry.apply(lambda geom: geom.wkb)
    # Count how many items are in each group.
    # The count only needs to look at one column, so the wkb column is used as it should always have a value.
    logger.debug("Finding intersection sizes")
    intersection['intersection_size'] = intersection.groupby('wkb')['wkb'].transform('size')

    # Filter to items that had at least three points at the intersection and remove any duplicates
    logger.debug("Filtering to only valid intersections (count >= %s)", junction_min_point_count)
    intersection = (intersection[intersection['intersection_size'] >= junction_min_point_count]
                    .drop_duplicates(subset=['intersection_size','wkb']))

    # Classify each point as an intersection
    logger.debug("Assigning 'Intersection' type to junctions")
    intersection[type_field_name] = 'Intersection'

    # Drop all the extra columns
    intersection = intersection.filter(['geometry', type_field_name])

    return intersection

def get_graph_for_lines(df, simplify=True):
    """Convert a GeoDataFrame consisting of linear features into a DiGraph."""
    # Only lines and multilines are supported
    if not df.type.isin(['LineString', 'MultiLineString']).all():
        raise ValueError("Improper geometry type in GeoDataFrame")

    logger.debug("Creating DiGraph from %s lines", len(df))
    net = nx.DiGraph()

    def edges_from_line(geom, attrs, simplify=True):
        """Generate edges for each line in geom."""
        if geom.type == 'LineString':
            edge_attrs = attrs.copy()
            if simplify:
                yield (geom.coords[0], geom.coords[-1], edge_attrs)
            else:
                for i in range(len(geom.coords) - 1):
                    pt1 = geom.coords[i]
                    pt2 = geom.coords[i + 1]
                    yield (pt1, pt2, edge_attrs)
        elif geom.type == 'MultiLineString':
            for line in geom:
                yield from edges_from_line(line, attrs, simplify)
    
    # Iterate the features and add them to the graph
    for feature in df.iterfeatures():
        # Each feature is a __geo_interface__ dict
        geom = shape(feature['geometry'])
        attrs = feature['properties']

        for edge in edges_from_line(geom, attrs, simplify):
            e1, e2, attr = edge
            net.add_edge(e1, e2)
            net[e1][e2].update(attr)
    
    logger.debug("Graph with %s nodes and %s edges created", net.number_of_nodes(), net.number_of_edges())
    
    return net

def get_attribute_for_node(net: nx.DiGraph, node_id: tuple, attr: str, default: str = 'None'):
    """Pull an attribute value from edges associated with a given node.

    Multiple edges are likely to be connected, so this returns the first instance of a value. In the case that no
    value is found, the default is returned.
    """
    # The node may not be in the graph at all. Return the default in this case.
    if not net.has_node(node_id):
        logger.debug("Node %r not found in graph", node_id)
        return default

    # We're only interested in edges attached to the node, so get a subgraph to make analysis quicker
    subnet = net.subgraph(node_id)

    # Get the attribute for all edges connected to this node
    attr_values = nx.get_edge_attributes(subnet, attr)

    # Take the first value that isn't None.
    try:
        result = next(val for val in attr_values.values() if val not in ('None', None))
    except StopIteration:
        # If no value was found use the default.
        result = default
    
    return result