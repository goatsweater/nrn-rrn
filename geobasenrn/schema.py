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
#         width: value,
#         type: value
#     }
# }

# When a field is noted used by a particular format the name should be set to None.
schema = {
    'nid': {
        'gpkg': {'en': 'NID', 'fr': 'IDN'},
        'shp': {'en': 'NID', 'fr': 'IDN'},
        'gml': {'en': 'nid', 'fr': 'idn'},
        'kml': {'en': 'nid', 'fr': 'idn'},
        'width': 32,
        'type': ogr.OFTString
    },
    'credate': {
        'gpkg': {'en': 'CREDATE', 'fr': 'DATECRE'},
        'shp': {'en': 'CREDATE', 'fr': 'DATECRE'},
        'gml': {'en': 'creationDate', 'fr': 'dateCreation'},
        'kml': {'en': None, 'fr': None},
        'width': 8,
        'type': ogr.OFTString
    },
    'revdate': {
        'gpkg': {'en': 'REVDATE', 'fr': 'DATEREV'},
        'shp': {'en': 'REVDATE', 'fr': 'DATEREV'},
        'gml': {'en': 'revisionDate', 'fr': 'dateRevision'},
        'kml': {'en': None, 'fr': None},
        'width': 8,
        'type': ogr.OFTString
    },
    'datasetnam': {
        'gpkg': {'en': 'DATASETNAM', 'fr': 'NOMJEUDONN'},
        'shp': {'en': 'DATASETNAM', 'fr': 'NOMJEUDONN'},
        'gml': {'en': 'datasetName', 'fr': 'nomJeuDonnees'},
        'kml': {'en': None, 'fr': None},
        'width': 25,
        'type': ogr.OFTString
    },
    'acqtech': {
        'gpkg': {'en': 'ACQTECH', 'fr': 'TECHACQ'},
        'shp': {'en': 'ACQTECH', 'fr': 'TECHACQ'},
        'gml': {'en': 'acquisitionTechnique', 'fr': 'techniqueAcquisition'},
        'kml': {'en': None, 'fr': None},
        'width': 23,
        'type': ogr.OFTString
    },
    'specvers': {
        'gpkg': {'en': 'SPECVERS', 'fr': 'VERSNORMES'},
        'shp': {'en': 'SPECVERS', 'fr': 'VERSNORMES'},
        'gml': {'en': 'standardVersion', 'fr': 'versionNormes'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTReal
    },
    'metacover': {
        'gpkg': {'en': 'METACOVER', 'fr': 'COUVERMETA'},
        'shp': {'en': 'METACOVER', 'fr': 'COUVERMETA'},
        'gml': {'en': 'metadataCoverage', 'fr': 'couvertureMetadonnees'},
        'kml': {'en': None, 'fr': None},
        'width': 8,
        'type': ogr.OFTString
    },
    'accuracy': {
        'gpkg': {'en': 'ACCURACY', 'fr': 'PRECISION'},
        'shp': {'en': 'ACCURACY', 'fr': 'PRECISION'},
        'gml': {'en': 'planimetricAccuracy', 'fr': 'precisionPlanimetrique'},
        'kml': {'en': None, 'fr': None},
        'width': 4,
        'type': ogr.OFTInteger
    },
    'provider': {
        'gpkg': {'en': 'PROVIDER', 'fr': 'FOURNISSR'},
        'shp': {'en': 'PROVIDER', 'fr': 'FOURNISSR'},
        'gml': {'en': 'provider', 'fr': 'fournisseur'},
        'kml': {'en': None, 'fr': None},
        'width': 24,
        'type': ogr.OFTString
    },
    'l_altnamnid': {
        'gpkg': {'en': 'L_ALTNANID', 'fr': 'IDNOMNOF_G'},
        'shp': {'en': 'L_ALTNANID', 'fr': 'IDNOMNOF_G'},
        'gml': {'en': 'left_AlternateStreetNameNid', 'fr': 'idnNomRueNonOfficiel_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 32,
        'type': ogr.OFTString
    },
    'r_altnamnid': {
        'gpkg': {'en': 'R_ALTNANID', 'fr': 'IDNOMNOF_D'},
        'shp': {'en': 'R_ALTNANID', 'fr': 'IDNOMNOF_D'},
        'gml': {'en': 'right_AlternateStreetNameNid', 'fr': 'idnNomRueNonOfficiel_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 32,
        'type': ogr.OFTString
    },
    'l_digdirfg': {
        'gpkg': {'en': 'L_DIGDIRFG', 'fr': 'SENSNUM_G'},
        'shp': {'en': 'L_DIGDIRFG', 'fr': 'SENSNUM_G'},
        'gml': {'en': 'left_DigitizingDirectionFlag', 'fr': 'sensNumerisation_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 18,
        'type': ogr.OFTString
    },
    'r_digdirfg': {
        'gpkg': {'en': 'R_DIGDIRFG', 'fr': 'SENSNUM_D'},
        'shp': {'en': 'R_DIGDIRFG', 'fr': 'SENSNUM_D'},
        'gml': {'en': 'right_DigitizingDirectionFlag', 'fr': 'sensNumerisation_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 18,
        'type': ogr.OFTString
    },
    'l_hnumf': {
        'gpkg': {'en': 'L_HNUMF', 'fr': 'NUMP_G'},
        'shp': {'en': 'L_HNUMF', 'fr': 'NUMP_G'},
        'gml': {'en': 'left_FirstHouseNumber', 'fr': 'numPremiereMaison_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 9,
        'type': ogr.OFTString
    },
    'r_hnumf': {
        'gpkg': {'en': 'R_HNUMF', 'fr': 'NUMP_D'},
        'shp': {'en': 'R_HNUMF', 'fr': 'NUMP_D'},
        'gml': {'en': 'right_FirstHouseNumber', 'fr': 'numPremiereMaison_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 9,
        'type': ogr.OFTString
    },
    'l_hnumsuff': {
        'gpkg': {'en': 'L_HNUMSUFF', 'fr': 'SUFNUMP_G'},
        'shp': {'en': 'L_HNUMSUFF', 'fr': 'SUFNUMP_G'},
        'gml': {'en': 'left_FirstHouseNumberSuffix', 'fr': 'suffixNumPremiereMaison_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'r_hnumsuff': {
        'gpkg': {'en': 'R_HNUMSUFF', 'fr': 'SUFNUMP_D'},
        'shp': {'en': 'R_HNUMSUFF', 'fr': 'SUFNUMP_D'},
        'gml': {'en': 'right_FirstHouseNumberSuffix', 'fr': 'suffixNumPremiereMaison_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'l_hnumtypf': {
        'gpkg': {'en': 'L_HNUMTYPF', 'fr': 'TYPENUMP_G'},
        'shp': {'en': 'L_HNUMTYPF', 'fr': 'TYPENUMP_G'},
        'gml': {'en': 'left_FirstHouseNumberType', 'fr': 'typeNumPremiereMaison_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 16,
        'type': ogr.OFTString
    },
    'r_hnumtypf': {
        'gpkg': {'en': 'R_HNUMTYPF', 'fr': 'TYPENUMP_D'},
        'shp': {'en': 'R_HNUMTYPF', 'fr': 'TYPENUMP_D'},
        'gml': {'en': 'right_FirstHouseNumberType', 'fr': 'typeNumPremiereMaison_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 16,
        'type': ogr.OFTString
    },
    'l_hnumstr': {
        'gpkg': {'en': 'L_HNUMSTR', 'fr': 'STRUNUM_G'},
        'shp': {'en': 'L_HNUMSTR', 'fr': 'STRUNUM_G'},
        'gml': {'en': 'left_HouseNumberStructure', 'fr': 'structureNumMaison_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 9,
        'type': ogr.OFTString
    },
    'r_hnumstr': {
        'gpkg': {'en': 'R_HNUMSTR', 'fr': 'STRUNUM_D'},
        'shp': {'en': 'R_HNUMSTR', 'fr': 'STRUNUM_D'},
        'gml': {'en': 'right_HouseNumberStructure', 'fr': 'structureNumMaison_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 9,
        'type': ogr.OFTString
    },
    'l_hnuml': {
        'gpkg': {'en': 'L_HNUML', 'fr': 'NUMD_G'},
        'shp': {'en': 'L_HNUML', 'fr': 'NUMD_G'},
        'gml': {'en': 'left_LastHouseNumber', 'fr': 'numDerniereMaison_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 9,
        'type': ogr.OFTString
    },
    'r_hnuml': {
        'gpkg': {'en': 'R_HNUML', 'fr': 'NUMD_D'},
        'shp': {'en': 'R_HNUML', 'fr': 'NUMD_D'},
        'gml': {'en': 'right_LastHouseNumber', 'fr': 'numDerniereMaison_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 9,
        'type': ogr.OFTString
    },
    'l_hnumsufl': {
        'gpkg': {'en': 'L_HNUMSUFL', 'fr': 'SUFNUMD_G'},
        'shp': {'en': 'L_HNUMSUFL', 'fr': 'SUFNUMD_G'},
        'gml': {'en': 'left_LastHouseNumberSuffix', 'fr': 'suffixNumDerniereMaison_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'r_hnumsufl': {
        'gpkg': {'en': 'R_HNUMSUFL', 'fr': 'SUFNUMD_D'},
        'shp': {'en': 'R_HNUMSUFL', 'fr': 'SUFNUMD_D'},
        'gml': {'en': 'right_LastHouseNumberSuffix', 'fr': 'suffixNumDerniereMaison_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'l_hnumtypl': {
        'gpkg': {'en': 'L_HNUMTYPL', 'fr': 'TYPENUMD_G'},
        'shp': {'en': 'L_HNUMTYPL', 'fr': 'TYPENUMD_G'},
        'gml': {'en': 'left_LastHouseNumberType', 'fr': 'typeNumDerniereMaison_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 16,
        'type': ogr.OFTString
    },
    'r_hnumtypl': {
        'gpkg': {'en': 'R_HNUMTYPL', 'fr': 'TYPENUMD_D'},
        'shp': {'en': 'R_HNUMTYPL', 'fr': 'TYPENUMD_D'},
        'gml': {'en': 'right_LastHouseNumberType', 'fr': 'typeNumDerniereMaison_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 16,
        'type': ogr.OFTString
    },
    'l_offnanid': {
        'gpkg': {'en': 'L_OFFNANID', 'fr': 'IDNOMOFF_G'},
        'shp': {'en': 'L_OFFNANID', 'fr': 'IDNOMOFF_G'},
        'gml': {'en': 'left_OfficialStreetNameNid', 'fr': 'idnNomRueOfficiel_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 32,
        'type': ogr.OFTString
    },
    'r_offnanid': {
        'gpkg': {'en': 'R_OFFNANID', 'fr': 'IDNOMOFF_D'},
        'shp': {'en': 'R_OFFNANID', 'fr': 'IDNOMOFF_D'},
        'gml': {'en': 'right_OfficialStreetNameNid', 'fr': 'idnNomRueOfficiel_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 32,
        'type': ogr.OFTString
    },
    'l_rfsysind': {
        'gpkg': {'en': 'L_RFSYSIND', 'fr': 'SYSREF_G'},
        'shp': {'en': 'L_RFSYSIND', 'fr': 'SYSREF_G'},
        'gml': {'en': 'left_ReferenceSystemIndicator', 'fr': 'indicSystemeReference_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 18,
        'type': ogr.OFTString
    },
    'r_rfsysind': {
        'gpkg': {'en': 'R_RFSYSIND', 'fr': 'SYSREF_D'},
        'shp': {'en': 'R_RFSYSIND', 'fr': 'SYSREF_D'},
        'gml': {'en': 'right_ReferenceSystemIndicator', 'fr': 'indicSystemeReference_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 18,
        'type': ogr.OFTString
    },
    'strnamenid': {
        'gpkg': {'en': 'STRNAMENID', 'fr': 'IDNOMRUE'},
        'shp': {'en': 'STRNAMENID', 'fr': 'IDNOMRUE'},
        'gml': {'en': 'streetNameNid', 'fr': 'idnNomRue'},
        'kml': {'en': None, 'fr': None},
        'width': 32,
        'type': ogr.OFTString
    },
    'blkpassty': {
        'gpkg': {'en': 'BLKPASSTY', 'fr': 'TYPEOBSTRU'},
        'shp': {'en': 'BLKPASSTY', 'fr': 'TYPEOBSTRU'},
        'gml': {'en': 'blockedPassageType', 'fr': 'typePassageObstrue'},
        'kml': {'en': None, 'fr': None},
        'width': 17,
        'type': ogr.OFTString
    },
    'roadnid': {
        'gpkg': {'en': 'ROADNID', 'fr': 'IDNELEMRTE'},
        'shp': {'en': 'ROADNID', 'fr': 'IDNELEMRTE'},
        'gml': {'en': 'roadElementNid', 'fr': 'idnElementRoutier'},
        'kml': {'en': None, 'fr': None},
        'width': 32,
        'type': ogr.OFTString
    },
    'closing': {
        'gpkg': {'en': 'CLOSING', 'fr': 'FERMETURE'},
        'shp': {'en': 'CLOSING', 'fr': 'FERMETURE'},
        'gml': {'en': 'closingPeriod', 'fr': 'periodeFermeture'},
        'kml': {'en': None, 'fr': None},
        'width': 7,
        'type': ogr.OFTString
    },
    'ferrysegid': {
        'gpkg': {'en': 'FERRYSEGID', 'fr': 'IDSEGMLTR'},
        'shp': {'en': 'FERRYSEGID', 'fr': 'IDSEGMLTR'},
        'gml': {'en': 'ferrySegmentId', 'fr': 'idSegmentLiaisonTransbordeur'},
        'kml': {'en': None, 'fr': None},
        'width': 9,
        'type': ogr.OFTInteger
    },
    'roadclass': {
        'gpkg': {'en': 'ROADCLASS', 'fr': 'CLASSROUTE'},
        'shp': {'en': 'ROADCLASS', 'fr': 'CLASSROUTE'},
        'gml': {'en': 'functionalRoadClass', 'fr': 'classRoutiereFonctionnelle'},
        'kml': {'en': None, 'fr': None},
        'width': 21,
        'type': ogr.OFTString
    },
    'rtename1en': {
        'gpkg': {'en': 'RTENAME1EN', 'fr': 'NOMRTE1AN'},
        'shp': {'en': 'RTENAME1EN', 'fr': 'NOMRTE1AN'},
        'gml': {'en': 'routeNameEnglish1', 'fr': 'nomRouteAnglais1'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename2en': {
        'gpkg': {'en': 'RTENAME2EN', 'fr': 'NOMRTE2AN'},
        'shp': {'en': 'RTENAME2EN', 'fr': 'NOMRTE2AN'},
        'gml': {'en': 'routeNameEnglish2', 'fr': 'nomRouteAnglais2'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename3en': {
        'gpkg': {'en': 'RTENAME3EN', 'fr': 'NOMRTE3AN'},
        'shp': {'en': 'RTENAME3EN', 'fr': 'NOMRTE3AN'},
        'gml': {'en': 'routeNameEnglish3', 'fr': 'nomRouteAnglais3'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename4en': {
        'gpkg': {'en': 'RTENAME4EN', 'fr': 'NOMRTE4AN'},
        'shp': {'en': 'RTENAME4EN', 'fr': 'NOMRTE4AN'},
        'gml': {'en': 'routeNameEnglish4', 'fr': 'nomRouteAnglais4'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename1fr': {
        'gpkg': {'en': 'RTENAME1FR', 'fr': 'NOMRTE1FR'},
        'shp': {'en': 'RTENAME1FR', 'fr': 'NOMRTE1FR'},
        'gml': {'en': 'routeNameFrench1', 'fr': 'nomRouteFrançais1'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename2fr': {
        'gpkg': {'en': 'RTENAME2FR', 'fr': 'NOMRTE2FR'},
        'shp': {'en': 'RTENAME2FR', 'fr': 'NOMRTE2FR'},
        'gml': {'en': 'routeNameFrench2', 'fr': 'nomRouteFrançais2'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename3fr': {
        'gpkg': {'en': 'RTENAME3FR', 'fr': 'NOMRTE3FR'},
        'shp': {'en': 'RTENAME3FR', 'fr': 'NOMRTE3FR'},
        'gml': {'en': 'routeNameFrench3', 'fr': 'nomRouteFrançais3'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtename4fr': {
        'gpkg': {'en': 'RTENAME4FR', 'fr': 'NOMRTE4FR'},
        'shp': {'en': 'RTENAME4FR', 'fr': 'NOMRTE4FR'},
        'gml': {'en': 'routeNameFrench4', 'fr': 'nomRouteFrançais4'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'rtnumber1': {
        'gpkg': {'en': 'RTNUMBER1', 'fr': 'NUMROUTE1'},
        'shp': {'en': 'RTNUMBER1', 'fr': 'NUMROUTE1'},
        'gml': {'en': 'routeNumber1', 'fr': 'numeroRoute1'},
        'kml': {'en': 'routeNumber1', 'fr': 'numeroRoute1'},
        'width': 10,
        'type': ogr.OFTString
    },
    'rtnumber2': {
        'gpkg': {'en': 'RTNUMBER2', 'fr': 'NUMROUTE2'},
        'shp': {'en': 'RTNUMBER2', 'fr': 'NUMROUTE2'},
        'gml': {'en': 'routeNumber2', 'fr': 'numeroRoute2'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'rtnumber3': {
        'gpkg': {'en': 'RTNUMBER3', 'fr': 'NUMROUTE3'},
        'shp': {'en': 'RTNUMBER3', 'fr': 'NUMROUTE3'},
        'gml': {'en': 'routeNumber3', 'fr': 'numeroRoute3'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'rtnumber4': {
        'gpkg': {'en': 'RTNUMBER4', 'fr': 'NUMROUTE4'},
        'shp': {'en': 'RTNUMBER4', 'fr': 'NUMROUTE4'},
        'gml': {'en': 'routeNumber4', 'fr': 'numeroRoute4'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'rtnumber5': {
        'gpkg': {'en': 'RTNUMBER5', 'fr': 'NUMROUTE5'},
        'shp': {'en': 'RTNUMBER5', 'fr': 'NUMROUTE5'},
        'gml': {'en': 'routeNumber5', 'fr': 'numeroRoute5'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'exitnbr': {
        'gpkg': {'en': 'EXITNBR', 'fr': 'NUMSORTIE'},
        'shp': {'en': 'EXITNBR', 'fr': 'NUMSORTIE'},
        'gml': {'en': 'exitNumber', 'fr': 'numeroSortie'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'junctype': {
        'gpkg': {'en': 'JUNCTYPE', 'fr': 'TYPEJONC'},
        'shp': {'en': 'JUNCTYPE', 'fr': 'TYPEJONC'},
        'gml': {'en': 'junctionType', 'fr': 'typeJonction'},
        'kml': {'en': None, 'fr': None},
        'width': 12,
        'type': ogr.OFTString
    },
    'l_adddirfg': {
        'gpkg': {'en': 'L_ADDDIRFG', 'fr': 'ADRSENS_G'},
        'shp': {'en': 'L_ADDDIRFG', 'fr': 'ADRSENS_G'},
        'gml': {'en': 'left_AddressDirectionFlag', 'fr': 'sensNumerisationAdresse_Gauche'},
        'kml': {'en': 'left_AddressDirectionFlag', 'fr': 'sensNumerisationAdresse_Gauche'},
        'width': 18,
        'type': ogr.OFTString
    },
    'r_adddirfg': {
        'gpkg': {'en': 'R_ADDDIRFG', 'fr': 'ADRSENS_D'},
        'shp': {'en': 'R_ADDDIRFG', 'fr': 'ADRSENS_D'},
        'gml': {'en': 'right_AddressDirectionFlag', 'fr': 'sensNumerisationAdresse_Droite'},
        'kml': {'en': 'right_AddressDirectionFlag', 'fr': 'sensNumerisationAdresse_Droite'},
        'width': 18,
        'type': ogr.OFTString
    },
    'adrangenid': {
        'gpkg': {'en': 'ADRANGENID', 'fr': 'IDINTERVAD'},
        'shp': {'en': 'ADRANGENID', 'fr': 'IDINTERVAD'},
        'gml': {'en': 'addressRangeNid', 'fr': 'idnIntervalleAdresse'},
        'kml': {'en': None, 'fr': None},
        'width': 32,
        'type': ogr.OFTString
    },
    'nbrlanes': {
        'gpkg': {'en': 'NBRLANES', 'fr': 'NBRVOIES'},
        'shp': {'en': 'NBRLANES', 'fr': 'NBRVOIES'},
        'gml': {'en': 'numberLanes', 'fr': 'nombreVoies'},
        'kml': {'en': None, 'fr': None},
        'width': 4,
        'type': ogr.OFTInteger
    },
    'l_placenam': {
        'gpkg': {'en': 'L_PLACENAM', 'fr': 'NOMLIEU_G'},
        'shp': {'en': 'L_PLACENAM', 'fr': 'NOMLIEU_G'},
        'gml': {'en': 'left_OfficialPlaceName', 'fr': 'nomLieuOfficiel_Gauche'},
        'kml': {'en': 'left_OfficialPlaceName', 'fr': 'nomLieuOfficiel_Gauche'},
        'width': 100,
        'type': ogr.OFTString
    },
    'r_placenam': {
        'gpkg': {'en': 'R_PLACENAM', 'fr': 'NOMLIEU_D'},
        'shp': {'en': 'R_PLACENAM', 'fr': 'NOMLIEU_D'},
        'gml': {'en': 'right_OfficialPlaceName', 'fr': 'nomLieuOfficiel_Droite'},
        'kml': {'en': 'right_OfficialPlaceName', 'fr': 'nomLieuOfficiel_Droite'},
        'width': 100,
        'type': ogr.OFTString
    },
    'l_stname_c': {
        'gpkg': {'en': 'L_STNAME_C', 'fr': 'NOMRUE_C_G'},
        'shp': {'en': 'L_STNAME_C', 'fr': 'NOMRUE_C_G'},
        'gml': {'en': 'left_OfficialStreetNameConcat', 'fr': 'nomRueOfficielConcat_Gauche'},
        'kml': {'en': 'left_OfficialStreetNameConcat', 'fr': 'nomRueOfficielConcat_Gauche'},
        'width': 100,
        'type': ogr.OFTString
    },
    'r_stname_c': {
        'gpkg': {'en': 'R_STNAME_C', 'fr': 'NOMRUE_C_D'},
        'shp': {'en': 'R_STNAME_C', 'fr': 'NOMRUE_C_D'},
        'gml': {'en': 'right_OfficialStreetNameConcat', 'fr': 'nomRueOfficielConcat_Droite'},
        'kml': {'en': 'right_OfficialStreetNameConcat', 'fr': 'nomRueOfficielConcat_Droite'},
        'width': 100,
        'type': ogr.OFTString
    },
    'pavsurf': {
        'gpkg': {'en': 'PAVSURF', 'fr': 'TYPEREV'},
        'shp': {'en': 'PAVSURF', 'fr': 'TYPEREV'},
        'gml': {'en': 'pavedRoadSurfaceType', 'fr': 'typeChausseeRevetue'},
        'kml': {'en': None, 'fr': None},
        'width': 8,
        'type': ogr.OFTString
    },
    'pavstatus': {
        'gpkg': {'en': 'PAVSTATUS', 'fr': 'ETATREV'},
        'shp': {'en': 'PAVSTATUS', 'fr': 'ETATREV'},
        'gml': {'en': 'pavementStatus', 'fr': 'etatRevetement'},
        'kml': {'en': None, 'fr': None},
        'width': 7,
        'type': ogr.OFTString
    },
    'roadjuris': {
        'gpkg': {'en': 'ROADJURIS', 'fr': 'AUTORITE'},
        'shp': {'en': 'ROADJURIS', 'fr': 'AUTORITE'},
        'gml': {'en': 'roadJurisdiction', 'fr': 'autoriteRoute'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'roadsegid': {
        'gpkg': {'en': 'ROADSEGID', 'fr': 'IDSEGMRTE'},
        'shp': {'en': 'ROADSEGID', 'fr': 'IDSEGMRTE'},
        'gml': {'en': 'roadSegmentId', 'fr': 'idSegmentRoutier'},
        'kml': {'en': None, 'fr': None},
        'width': 9,
        'type': ogr.OFTInteger
    },
    'speed': {
        'gpkg': {'en': 'SPEED', 'fr': 'VITESSE'},
        'shp': {'en': 'SPEED', 'fr': 'VITESSE'},
        'gml': {'en': 'speedRestrictions', 'fr': 'limitesVitesse'},
        'kml': {'en': None, 'fr': None},
        'width': 4,
        'type': ogr.OFTInteger
    },
    'strunameen': {
        'gpkg': {'en': 'STRUNAMEEN', 'fr': 'NOMSTRUCAN'},
        'shp': {'en': 'STRUNAMEEN', 'fr': 'NOMSTRUCAN'},
        'gml': {'en': 'structureNameEnglish', 'fr': 'nomStructureAnglais'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'strunamefr': {
        'gpkg': {'en': 'STRUNAMEFR', 'fr': 'NOMSTRUCFR'},
        'shp': {'en': 'STRUNAMEFR', 'fr': 'NOMSTRUCFR'},
        'gml': {'en': 'structureNameFrench', 'fr': 'nomStructureFrançais'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'structid': {
        'gpkg': {'en': 'STRUCTID', 'fr': 'IDSTRUCT'},
        'shp': {'en': 'STRUCTID', 'fr': 'IDSTRUCT'},
        'gml': {'en': 'structureId', 'fr': 'idStructure'},
        'kml': {'en': None, 'fr': None},
        'width': 32,
        'type': ogr.OFTString
    },
    'structtype': {
        'gpkg': {'en': 'STRUCTTYPE', 'fr': 'TYPESTRUCT'},
        'shp': {'en': 'STRUCTTYPE', 'fr': 'TYPESTRUCT'},
        'gml': {'en': 'structureType', 'fr': 'typeStructure'},
        'kml': {'en': None, 'fr': None},
        'width': 15,
        'type': ogr.OFTString
    },
    'trafficdir': {
        'gpkg': {'en': 'TRAFFICDIR', 'fr': 'SENSCIRCUL'},
        'shp': {'en': 'TRAFFICDIR', 'fr': 'SENSCIRCUL'},
        'gml': {'en': 'trafficDirection', 'fr': 'sensCirculation'},
        'kml': {'en': None, 'fr': None},
        'width': 18,
        'type': ogr.OFTString
    },
    'unpavsurf': {
        'gpkg': {'en': 'UNPAVSURF', 'fr': 'TYPENONREV'},
        'shp': {'en': 'UNPAVSURF', 'fr': 'TYPENONREV'},
        'gml': {'en': 'unpavedRoadSurfaceType', 'fr': 'typeChausseeNonRevetue'},
        'kml': {'en': None, 'fr': None},
        'width': 7,
        'type': ogr.OFTString
    },
    'dirprefix': {
        'gpkg': {'en': 'DIRPREFIX', 'fr': 'PREDIR'},
        'shp': {'en': 'DIRPREFIX', 'fr': 'PREDIR'},
        'gml': {'en': 'directionalPrefix', 'fr': 'prefixeDirection'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'dirsuffix': {
        'gpkg': {'en': 'DIRSUFFIX', 'fr': 'SUFDIR'},
        'shp': {'en': 'DIRSUFFIX', 'fr': 'SUFDIR'},
        'gml': {'en': 'directionalSuffix', 'fr': 'suffixeDirection'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'muniquad': {
        'gpkg': {'en': 'MUNIQUAD', 'fr': 'MUNIQUAD'},
        'shp': {'en': 'MUNIQUAD', 'fr': 'MUNIQUAD'},
        'gml': {'en': 'muniQuadrant', 'fr': 'muniQuadrant'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString
    },
    'placename': {
        'gpkg': {'en': 'PLACENAME', 'fr': 'NOMLIEU'},
        'shp': {'en': 'PLACENAME', 'fr': 'NOMLIEU'},
        'gml': {'en': 'placeName', 'fr': 'nomLieu'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'placetype': {
        'gpkg': {'en': 'PLACETYPE', 'fr': 'TYPELIEU'},
        'shp': {'en': 'PLACETYPE', 'fr': 'TYPELIEU'},
        'gml': {'en': 'placeType', 'fr': 'typeLieu'},
        'kml': {'en': None, 'fr': None},
        'width': 100,
        'type': ogr.OFTString
    },
    'province': {
        'gpkg': {'en': 'PROVINCE', 'fr': 'PROVINCE'},
        'shp': {'en': 'PROVINCE', 'fr': 'PROVINCE'},
        'gml': {'en': 'province', 'fr': 'province'},
        'kml': {'en': None, 'fr': None},
        'width': 25,
        'type': ogr.OFTString
    },
    'starticle': {
        'gpkg': {'en': 'STARTICLE', 'fr': 'ARTNOMRUE'},
        'shp': {'en': 'STARTICLE', 'fr': 'ARTNOMRUE'},
        'gml': {'en': 'streetNameArticle', 'fr': 'articleNomRue'},
        'kml': {'en': None, 'fr': None},
        'width': 20,
        'type': ogr.OFTString
    },
    'namebody': {
        'gpkg': {'en': 'NAMEBODY', 'fr': 'CORPSNOM'},
        'shp': {'en': 'NAMEBODY', 'fr': 'CORPSNOM'},
        'gml': {'en': 'streetNameBody', 'fr': 'corpsNomRue'},
        'kml': {'en': None, 'fr': None},
        'width': 50,
        'type': ogr.OFTString
    },
    'strtypre': {
        'gpkg': {'en': 'STRTYPRE', 'fr': 'PRETYPRUE'},
        'shp': {'en': 'STRTYPRE', 'fr': 'PRETYPRUE'},
        'gml': {'en': 'streetTypePrefix', 'fr': 'prefixeTypeRue'},
        'kml': {'en': None, 'fr': None},
        'width': 30,
        'type': ogr.OFTString
    },
    'strtysuf': {
        'gpkg': {'en': 'STRTYSUF', 'fr': 'SUFTYPRUE'},
        'shp': {'en': 'STRTYSUF', 'fr': 'SUFTYPRUE'},
        'gml': {'en': 'streetTypeSuffix', 'fr': 'suffixeTypeRue'},
        'kml': {'en': None, 'fr': None},
        'width': 30,
        'type': ogr.OFTString
    },
    'tollpttype': {
        'gpkg': {'en': 'TOLLPTTYPE', 'fr': 'TYPEPTEPEA'},
        'shp': {'en': 'TOLLPTTYPE', 'fr': 'TYPEPTEPEA'},
        'gml': {'en': 'tollPointType', 'fr': 'typePassageObstrue'},
        'kml': {'en': None, 'fr': None},
        'width': 22,
        'type': ogr.OFTString
    },
}
