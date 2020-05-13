"""Define schema information for fields across each supported format."""

from osgeo import ogr

__all__ = ['schema']

# Schema information for all the fields across the dataset
# {
#     field: {
#         format: {
#             en: name,
#             fr: name
#         },
#         width: value
#     }
# }
schema = {
    'nid': {
        'gpkg': {'en': 'NID', 'fr': 'IDN'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 32,
        'type': ogr.OFTString
    },
    'credate': {
        'gpkg': {'en': 'CREDATE', 'fr': 'DATECRE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 8,
        'type': ogr.OFTString
    },
    'revdate': {
        'gpkg': {'en': 'REVDATE', 'fr': 'DATEREV'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 8,
        'type': ogr.OFTString
    },
    'datasetnam': {
        'gpkg': {'en': 'DATASETNAM', 'fr': 'NOMJEUDONN'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 25,
        'type': ogr.OFTString
    },
    'acqtech': {
        'gpkg': {'en': 'ACQTECH', 'fr': 'TECHACQ'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 23,
        'type': ogr.OFTString
    },
    'specvers': {
        'gpkg': {'en': 'SPECVERS', 'fr': 'VERSNORMES'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTReal
    },
    'metacover': {
        'gpkg': {'en': 'METACOVER', 'fr': 'COUVERMETA'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 8,
        'type': ogr.OFTString
    },
    'accuracy': {
        'gpkg': {'en': 'ACCURACY', 'fr': 'PRECISION'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 4,
        'type': ogr.OFTInteger
    },
    'provider': {
        'gpkg': {'en': 'PROVIDER', 'fr': 'FOURNISSR'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 24,
        'type': ogr.OFTString
    },
    'l_altnamnid': {
        'gpkg': {'en': 'L_ALTNANID', 'fr': 'IDNOMNOF_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 32,
        'type': ogr.OFTString
    },
    'r_altnamnid': {
        'gpkg': {'en': 'R_ALTNANID', 'fr': 'IDNOMNOF_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 32,
        'type': ogr.OFTString
    },
    'l_digdirfg': {
        'gpkg': {'en': 'L_DIGDIRFG', 'fr': 'SENSNUM_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 18,
        'type': ogr.OFTString
    },
    'r_digdirfg': {
        'gpkg': {'en': 'R_DIGDIRFG', 'fr': 'SENSNUM_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 18,
        'type': ogr.OFTString
    },
    'l_hnumf': {
        'gpkg': {'en': 'L_HNUMF', 'fr': 'NUMP_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 9,
        'type': ogr.OFTString
    },
    'r_hnumf': {
        'gpkg': {'en': 'R_HNUMF', 'fr': 'NUMP_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 9,
        'type': ogr.OFTString
    },
    'l_hnumsuff': {
        'gpkg': {'en': 'L_HNUMSUFF', 'fr': 'SUFNUMP_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'r_hnumsuff': {
        'gpkg': {'en': 'R_HNUMSUFF', 'fr': 'SUFNUMP_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'l_hnumtypf': {
        'gpkg': {'en': 'L_HNUMTYPF', 'fr': 'TYPENUMP_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 16,
        'type': ogr.OFTString
    },
    'r_hnumtypf': {
        'gpkg': {'en': 'R_HNUMTYPF', 'fr': 'TYPENUMP_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 16,
        'type': ogr.OFTString
    },
    'l_hnumstr': {
        'gpkg': {'en': 'L_HNUMSTR', 'fr': 'STRUNUM_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 9,
        'type': ogr.OFTString
    },
    'r_hnumstr': {
        'gpkg': {'en': 'R_HNUMSTR', 'fr': 'STRUNUM_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 9,
        'type': ogr.OFTString
    },
    'l_hnuml': {
        'gpkg': {'en': 'L_HNUML', 'fr': 'NUMD_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 9,
        'type': ogr.OFTString
    },
    'r_hnuml': {
        'gpkg': {'en': 'R_HNUML', 'fr': 'NUMD_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 9,
        'type': ogr.OFTString
    },
    'l_hnumsufl': {
        'gpkg': {'en': 'L_HNUMSUFL', 'fr': 'SUFNUMD_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'r_hnumsufl': {
        'gpkg': {'en': 'R_HNUMSUFL', 'fr': 'SUFNUMD_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'l_hnumtypl': {
        'gpkg': {'en': 'L_HNUMTYPL', 'fr': 'TYPENUMD_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 16,
        'type': ogr.OFTString
    },
    'r_hnumtypl': {
        'gpkg': {'en': 'R_HNUMTYPL', 'fr': 'TYPENUMD_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 16,
        'type': ogr.OFTString
    },
    'l_offnanid': {
        'gpkg': {'en': 'L_OFFNANID', 'fr': 'IDNOMOFF_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 32,
        'type': ogr.OFTString
    },
    'r_offnanid': {
        'gpkg': {'en': 'R_OFFNANID', 'fr': 'IDNOMOFF_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 32,
        'type': ogr.OFTString
    },
    'l_rfsysind': {
        'gpkg': {'en': 'L_RFSYSIND', 'fr': 'SYSREF_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 18,
        'type': ogr.OFTString
    },
    'r_rfsysind': {
        'gpkg': {'en': 'R_RFSYSIND', 'fr': 'SYSREF_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 18,
        'type': ogr.OFTString
    },
    'strnamenid': {
        'gpkg': {'en': 'STRNAMENID', 'fr': 'IDNOMRUE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 32,
        'type': ogr.OFTString
    },
    'blkpassty': {
        'gpkg': {'en': 'BLKPASSTY', 'fr': 'TYPEOBSTRU'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 17,
        'type': ogr.OFTString
    },
    'roadnid': {
        'gpkg': {'en': 'ROADNID', 'fr': 'IDNELEMRTE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 32,
        'type': ogr.OFTString
    },
    'closing': {
        'gpkg': {'en': 'CLOSING', 'fr': 'FERMETURE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 7,
        'type': ogr.OFTString
    },
    'ferrysegid': {
        'gpkg': {'en': 'FERRYSEGID', 'fr': 'IDSEGMLTR'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 9,
        'type': ogr.OFTInteger
    },
    'roadclass': {
        'gpkg': {'en': 'ROADCLASS', 'fr': 'CLASSROUTE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 21,
        'type': ogr.OFTString
    },
    'rtename1en': {
        'gpkg': {'en': 'RTENAME1EN', 'fr': 'NOMRTE1AN'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename2en': {
        'gpkg': {'en': 'RTENAME2EN', 'fr': 'NOMRTE2AN'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename3en': {
        'gpkg': {'en': 'RTENAME3EN', 'fr': 'NOMRTE3AN'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename4en': {
        'gpkg': {'en': 'RTENAME4EN', 'fr': 'NOMRTE4AN'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename1fr': {
        'gpkg': {'en': 'RTENAME1FR', 'fr': 'NOMRTE1FR'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename2fr': {
        'gpkg': {'en': 'RTENAME2FR', 'fr': 'NOMRTE2FR'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename3fr': {
        'gpkg': {'en': 'RTENAME3FR', 'fr': 'NOMRTE3FR'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename4fr': {
        'gpkg': {'en': 'RTENAME4FR', 'fr': 'NOMRTE4FR'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtnumber1': {
        'gpkg': {'en': 'RTNUMBER1', 'fr': 'NUMROUTE1'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'rtnumber2': {
        'gpkg': {'en': 'RTNUMBER2', 'fr': 'NUMROUTE2'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'rtnumber3': {
        'gpkg': {'en': 'RTNUMBER3', 'fr': 'NUMROUTE3'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'rtnumber4': {
        'gpkg': {'en': 'RTNUMBER4', 'fr': 'NUMROUTE4'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'rtnumber5': {
        'gpkg': {'en': 'RTNUMBER5', 'fr': 'NUMROUTE5'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'exitnbr': {
        'gpkg': {'en': 'EXITNBR', 'fr': 'NUMSORTIE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'junctype': {
        'gpkg': {'en': 'JUNCTYPE', 'fr': 'TYPEJONC'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 12,
        'type': ogr.OFTString
    },
    'l_adddirfg': {
        'gpkg': {'en': 'L_ADDDIRFG', 'fr': 'ADRSENS_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 18,
        'type': ogr.OFTString
    },
    'r_adddirfg': {
        'gpkg': {'en': 'R_ADDDIRFG', 'fr': 'ADRSENS_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 18,
        'type': ogr.OFTString
    },
    'adrangenid': {
        'gpkg': {'en': 'ADRANGENID', 'fr': 'IDINTERVAD'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 32,
        'type': ogr.OFTString
    },
    'nbrlanes': {
        'gpkg': {'en': 'NBRLANES', 'fr': 'NBRVOIES'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 4,
        'type': ogr.OFTInteger
    },
    'l_placenam': {
        'gpkg': {'en': 'L_PLACENAM', 'fr': 'NOMLIEU_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'r_placenam': {
        'gpkg': {'en': 'R_PLACENAM', 'fr': 'NOMLIEU_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'l_stname_c': {
        'gpkg': {'en': 'L_STNAME_C', 'fr': 'NOMRUE_C_G'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'r_stname_c': {
        'gpkg': {'en': 'R_STNAME_C', 'fr': 'NOMRUE_C_D'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'pavsurf': {
        'gpkg': {'en': 'PAVSURF', 'fr': 'TYPEREV'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 8,
        'type': ogr.OFTString
    },
    'pavstatus': {
        'gpkg': {'en': 'PAVSTATUS', 'fr': 'ETATREV'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 7,
        'type': ogr.OFTString
    },
    'roadjuris': {
        'gpkg': {'en': 'ROADJURIS', 'fr': 'AUTORITE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'roadsegid': {
        'gpkg': {'en': 'ROADSEGID', 'fr': 'IDSEGMRTE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 9,
        'type': ogr.OFTInteger
    },
    'speed': {
        'gpkg': {'en': 'SPEED', 'fr': 'VITESSE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 4,
        'type': ogr.OFTInteger
    },
    'strunameen': {
        'gpkg': {'en': 'STRUNAMEEN', 'fr': 'NOMSTRUCAN'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'strunamefr': {
        'gpkg': {'en': 'STRUNAMEFR', 'fr': 'NOMSTRUCFR'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'structid': {
        'gpkg': {'en': 'STRUCTID', 'fr': 'IDSTRUCT'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 32,
        'type': ogr.OFTString
    },
    'structtype': {
        'gpkg': {'en': 'STRUCTTYPE', 'fr': 'TYPESTRUCT'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 15,
        'type': ogr.OFTString
    },
    'trafficdir': {
        'gpkg': {'en': 'TRAFFICDIR', 'fr': 'SENSCIRCUL'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 18,
        'type': ogr.OFTString
    },
    'unpavsurf': {
        'gpkg': {'en': 'UNPAVSURF', 'fr': 'TYPENONREV'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 7,
        'type': ogr.OFTString
    },
    'dirprefix': {
        'gpkg': {'en': 'DIRPREFIX', 'fr': 'PREDIR'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'dirsuffix': {
        'gpkg': {'en': 'DIRSUFFIX', 'fr': 'SUFDIR'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'muniquad': {
        'gpkg': {'en': 'MUNIQUAD', 'fr': 'MUNIQUAD'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 10,
        'type': ogr.OFTString
    },
    'placename': {
        'gpkg': {'en': 'PLACENAME', 'fr': 'NOMLIEU'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'placetype': {
        'gpkg': {'en': 'PLACETYPE', 'fr': 'TYPELIEU'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 100,
        'type': ogr.OFTString
    },
    'province': {
        'gpkg': {'en': 'PROVINCE', 'fr': 'PROVINCE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 25,
        'type': ogr.OFTString
    },
    'starticle': {
        'gpkg': {'en': 'STARTICLE', 'fr': 'ARTNOMRUE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 20,
        'type': ogr.OFTString
    },
    'namebody': {
        'gpkg': {'en': 'NAMEBODY', 'fr': 'CORPSNOM'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 50,
        'type': ogr.OFTString
    },
    'strtypre': {
        'gpkg': {'en': 'STRTYPRE', 'fr': 'PRETYPRUE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 30,
        'type': ogr.OFTString
    },
    'strtysuf': {
        'gpkg': {'en': 'STRTYSUF', 'fr': 'SUFTYPRUE'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 30,
        'type': ogr.OFTString
    },
    'tollpttype': {
        'gpkg': {'en': 'TOLLPTTYPE', 'fr': 'TYPEPTEPEA'},
        'shp': {'en': '', 'fr': ''},
        'gml': {'en': '', 'fr': ''},
        'kml': {'en': '', 'fr': ''},
        'width': 22,
        'type': ogr.OFTString
    },
}
