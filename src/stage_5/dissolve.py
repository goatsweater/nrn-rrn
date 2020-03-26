#!/usr/bin/env python3
import os
import sys
import warnings
from functools import wraps


def ignore_warnings(f):
    @wraps(f)
    def inner(*args, **kwargs):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("ignore")
            response = f(*args, **kwargs)
        return response
    return inner


def import_qgis_processing():
    sys.path.append('/usr/lib/qgis')
    sys.path.append('/usr/share/qgis/python/plugins')
    from qgis.core import QgsApplication, QgsProcessingFeedback, QgsRasterLayer
    app = QgsApplication([], False)
    feedback = QgsProcessingFeedback()
    return (app, feedback, QgsRasterLayer)


app, feedback, QgsRasterLayer = import_qgis_processing()
app.initQgis()


@ignore_warnings # Ignored because we want the output of this script to be a single value, and "import processing" is noisy
def initialise_processing(app):
    from qgis.analysis import QgsNativeAlgorithms
    import processing
    from processing.core.Processing import Processing
    Processing.initialize()
    app.processingRegistry().addProvider(QgsNativeAlgorithms())
    return (app, processing,)


def dissolve():
   params = {
            'FIELD': [''],
            'INPUT': '/home/kent/PycharmProjects/nrn-rrn/data/interim/merged.gpkg',
            'OUTPUT': '/home/kent/PycharmProjects/nrn-rrn/data/interim/dissolve.gpkg'
   }
   return processing.run("native:dissolve", {'INPUT':'/home/kent/PycharmProjects/nrn-rrn/data/interim/add_geom.gpkg|layername=add_geom','FIELD':[],'OUTPUT':'ogr:dbname=\'/home/kent/PycharmProjects/nrn-rrn/data/interim/dissolve.gpkg\' table=\"dissolve\" (geom)'})

app, processing = initialise_processing(app)
dissolve()
app.exitQgis()
