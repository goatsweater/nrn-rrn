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
    start_points = geo_df.geometry.apply(lambda geom: Point(geom.coords[0]))
    end_points = geo_df.geometry.apply(lambda geom: Point(geom.coords[-1]))
    # Concatenate all the points into one large series
    all_points = (pd.concat([start_points, end_points])
                  .dropna()
                  .drop_duplicates())
    # It is possible that somehow an empty geometry snuck in. Remove them.
    # all_points = all_points[~all_points.isna()]

    return all_points

def build_junctions(road_df, admin_boundary_poly, ferry_df = gpd.GeoDataFrame()):
    """Find all the junction points in the linear datasets and classify them according to NRN rules."""
    logger.debug("Calculating road intersections")
    type_field_name = 'junctype'
    # Look for road junctions first
    road_juncs = gpd.overlay(road_df, road_df, how='intersection', keep_geom_type=False)
    # Self intersections will create more than just points, but only the points are of interest
    road_juncs = road_juncs[road_juncs.geometry.type == 'Point']

    # There needs to be three or more points at an intersection.
    logger.debug("Getting road junctions")
    # You can't groupby on a geometry, so use the WKB representation
    logger.debug("Calculating WKB for each shape")
    road_juncs['wkb'] = road_juncs.geometry.apply(lambda geom: geom.wkb)
    # Count how many items are in each group.
    # The count only needs to look at one column, so the NID column is used as it should always have a value.
    logger.debug("Finding intersection sizes")
    road_juncs['intersection_size'] = road_juncs.groupby('wkb')['nid_1'].transform('size')

    # Filter to items that had at least three points at the intersection and remove any duplicates
    logger.debug("Filtering to only valid intersections (count >= 3)")
    road_juncs = (road_juncs[road_juncs['intersection_size'] > 2]
                  .drop_duplicates(subset='wkb'))
    road_juncs[type_field_name] = 'Intersection'
    

    # Gather all the start and end points into a list for later
    all_start_end_points = [
        _get_start_and_end_points(road_df)
    ]

    # Now look for ferry junctions, if ferry routes are provided
    if not ferry_df.empty:
        logger.debug("Getting ferry junctions")
        ferry_juncs = gpd.overlay(road_df, ferry_df, how='intersection', keep_geom_type=False)
        ferry_juncs[type_field_name] = 'Ferry'
        # Add the ferry start/end points to the all points list
        all_start_end_points.append(_get_start_and_end_points(ferry_df))

    # Dead-ends are the end of a line that does not intersect with anything else
    logger.debug("Finding dead-ends")

    all_start_end_points = pd.concat(all_start_end_points)
    dead_ends = gpd.GeoDataFrame({'geometry': all_start_end_points, 
                                  type_field_name: ['DeadEnd'] * len(all_start_end_points)})
    
    # Remove already found road and ferry junctions
    dead_ends = gpd.overlay(dead_ends, road_juncs, how='difference')
    dead_ends = gpd.overlay(dead_ends, ferry_juncs, how='difference')

    # Dead-ends outside the administrative boundary are classed as NatProvTer since they connect to a neighbour dataset
    logger.debug("Getting junctions at administrative boundaries")
    dead_ends.loc[~dead_ends.geometry.within(admin_boundary_poly), type_field_name] = 'NatProvTer'

    logger.debug("Calculating junction attributes")
    junctions = pd.concat([road_juncs.filter(['geometry', type_field_name]),
                           ferry_juncs.filter(['geometry', type_field_name]),
                           dead_ends])
    junctions["acqtech"] = "Computed"
    junctions["metacover"] = "Complete"
    junctions["specvers"] = nrn.__spec_version__
    junctions["credate"] = datetime.datetime.today().strftime("%Y%m%d")
    junctions["provider"] = "Federal"

    # Retrive a given attribute from associated edges
    net_graph = get_graph_for_lines(road_df)
    copy_attr_field = 'exitnbr'
    logger.debug("Looking for %s values", copy_attr_field)
    junctions[copy_attr_field] = junctions.geometry.apply(lambda geom: get_attribute_for_node(net_graph, 
                                                                                        geom.coords[0], 
                                                                                        copy_attr_field))
                                                                                        
    copy_attr_field = 'accuracy'
    logger.debug("Looking for %s values", copy_attr_field)
    junctions[copy_attr_field] = junctions.geometry.apply(lambda geom: get_attribute_for_node(net_graph, 
                                                                                        geom.coords[0], 
                                                                                        copy_attr_field))

    return junctions

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
        return default

    attr_values = nx.get_edge_attributes(net, attr)
    # Take the first value that isn't None.
    try:
        result = next(val for val in attr_values.values() if val is not None)
    except StopIteration:
        # If no value was found use the default.
        result = default
    
    return result