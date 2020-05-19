"""
National Road Network data conversion and processing.

Usage
-----

```
import geobasenrn as nrn
```

"""

# Default precision for coordinates
DEFAULT_PRECISION = 7

# EPSG code to be used for all GeoBase data
SRS_EPSG_CODE = 4617

spatial_layers = ['blkpassage', 'junction', 'tollpoint', 'ferryseg', 'roadseg']
attribute_layers = ['addrange', 'altnamlink', 'strplaname']