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

def build_junctions(road_df, admin_boundary_poly, ferry_df = gpd.GeoDataFrame()):
    """Find all the junction points in the linear datasets and classify them according to NRN rules."""
    logger.debug("Calculating junctions")

    # Column name to set for the junction type
    type_field_name = 'junctype'
    # Junctions are when at least three roads meet
    junction_min_point_count = 3

    # Create a network graph from the road network
    road_graph = get_graph_for_lines(road_df)

    # Set the intersection type on the nodes
    logger.debug("Getting road junctions")
    # Intersections are any node with a degree matching or higher than the junction minimum count
    # Everything with only one connection is set to dead end for now (some will be boundary or ferry)
    for node, degree in road_graph.degree():
        if degree >= junction_min_point_count:
            road_graph.nodes[node][type_field_name] = 'Intersection'
        elif degree == 1:
            road_graph.nodes[node][type_field_name] = 'DeadEnd'
    
    # If ferry data was provided, add those nodes to the road graph and update the end points accordingly
    if ferry_df is not None and not ferry_df.empty:
        logger.debug("Getting ferry junctions")
        ferry_graph = get_graph_for_lines(ferry_df)
        # Look for the nodes in the road graph and set them to type ferry
        for ferry_node in ferry_graph.nodes():
            if road_graph.has_node(ferry_node):
                road_graph.nodes[ferry_node][type_field_name] = 'Ferry'
            else:
                # If the node wasn't there, add it and don't bother connecting it to anything
                road_graph.add_node(ferry_node, **{type_field_name: 'Ferry'})
    
    # Convert the graph into a point GeoDataFrame, keeping the node attributes
    logger.debug("Gathering attributes for each junction")
    points = []
    for node, junctype in road_graph.nodes.data(type_field_name):
        # Skip anything that wasn't assigned a junction type as they aren't valid junctions
        if junctype is None:
            continue
        pnt = Point(node)
        # Retrive a given attribute from associated edges
        exitnbr = get_attribute_for_node(road_graph, node, 'exitnbr')
        accuracy = get_attribute_for_node(road_graph, node, 'accuracy', default=-1)
        # Save the data to be converted to a GeoDataFrame
        record = {'geometry': pnt, type_field_name: junctype, 'exitnbr': exitnbr, 'accuracy': accuracy}
        points.append(record)
    logger.debug("Building junctions GeoDataFrame")
    junctions = gpd.GeoDataFrame(points, crs=f'EPSG:{nrn.SRS_EPSG_CODE}')

    # Mark junctions along the admin boundary as a border crossing
    junctions.loc[~junctions.geometry.within(admin_boundary_poly), type_field_name] = 'NatProvTer'

    # Set remaining attributes on the data
    junctions["acqtech"] = "Computed"
    junctions["metacover"] = "Complete"
    junctions["specvers"] = nrn.__spec_version__
    junctions["credate"] = datetime.datetime.today().strftime("%Y%m%d")
    junctions["provider"] = "Federal"

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
        logger.debug("Node %r not found in graph", node_id)
        return default

    # DiGraphs have in and out edges, so we need to check both
    edge_list = []
    edge_list.extend(net.out_edges(node_id))
    edge_list.extend(net.in_edges(node_id))

    # We're only interested in edges attached to the node, so get a subgraph to make analysis quicker
    subnet = net.edge_subgraph(edge_list)

    # Get the desired attribute for all edges connected to this node
    attr_values = nx.get_edge_attributes(subnet, attr)

    # Take the first value that isn't None.
    try:
        result = next(val for val in attr_values.values() if val not in ('None', None))
    except StopIteration:
        # If no value was found use the default.
        result = default
    
    return result