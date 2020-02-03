import sys
import os
import geopandas as gpd
from shapely.ops import split, snap, linemerge, unary_union

sys.path.insert(1, os.path.join(sys.path[0], ".."))
import helpers

def split_line_by_nearest_points(gdf_line, gdf_points, tolerance):
    """
    Split the union of lines with the union of points resulting
    Parameters
    ----------
    gdf_line : geoDataFrame
        geodataframe with multiple rows of connecting line segments
    gdf_points : geoDataFrame
        geodataframe with multiple rows of single points

    Returns
    -------
    gdf_segments : geoDataFrame
        geodataframe of segments
    """

    gdf_line["diss"] = "1"
    line = gdf_line.dissolve(by="diss")

    # union all geometries
    line = gdf_line.geometry.unary_union
    line = linemerge(line)
    coords = gdf_points.geometry.unary_union

    # snap and split coords on line
    # returns GeometryCollection
    split_line = split(line, snap(coords, line, tolerance))

    # transform Geometry Collection to GeoDataFrame
    segments = [feature for feature in split_line]

    gdf_segments = gpd.GeoDataFrame(
        list(range(len(segments))), geometry=segments)
    gdf_segments.columns = ['index', 'geometry']

    return gdf_segments

print("Reading...")
points = gpd.read_file("C:/Users/jacoken/PycharmProjects/National_Road_Network/data/interim/nb.gpkg", layer="junction", driver="GPKG")
lines = gpd.read_file("C:/Users/jacoken/PycharmProjects/National_Road_Network/data/interim/nb.gpkg", layer="roadseg", driver="GPKG")

print("Splitting...")
split_lines = split_line_by_nearest_points(lines, points, tolerance=0.5)

print("Writing...")
split_lines.to_file("C:/Users/jacoken/PycharmProjects/National_Road_Network/data/interim/nb_test.gpkg", layer="split_lines", driver="GPKG")

print(len(split_lines))