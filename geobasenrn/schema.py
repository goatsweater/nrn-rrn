"""Define schema information for fields across each supported format."""

import logging
from osgeo import ogr

__all__ = ['schema', 'class_map']

logger = logging.getLogger(__name__)

# Some fields have a restricted set of values.
domains = {
    'acquisition_technique': {
        'en': {'Unknown': -1, 'None': 0, 'Other': 1, 'GPS': 2, 'Orthoimage': 3, 'Orthophoto': 4, 'Vector Data': 5, 'Paper Map': 6, 'Field Completion': 7, 'Raster Data': 8, 'Digital Elevation Model': 9, 'Aerial Photo': 10, 'Raw Imagery Data': 11, 'Computed': 12},
        'fr': {'Inconnu': -1, 'Aucun': 0, 'Autre': 1, 'GPS': 2, 'Ortho-image': 3, 'Ortho-photo': 4, 'Données vectorielles': 5, 'Carte papier': 6, 'Complètement terrain': 7, 'Données matricielles': 8, "Modèle numérique d'élévation": 9, 'Photographie aérienne': 10, 'Image satellite brute': 11, 'Calculé': 12}
    },
    'metadata_coverage': {
        'en': {'Unknown': -1, 'Complete': 1, 'Partial': 2},
        'fr': {'Inconnu': -1, 'Complet': 1, 'Partiel': 2}
    },
    'dataset_name': {
        'en': {'Newfoundland and Labrador': 1, 'Nova Scotia': 2, 'Prince Edward Island': 3, 'New Brunswick': 4, 'Quebec': 5, 'Ontario': 6, 'Manitoba': 7, 'Saskatchewan': 8, 'Alberta': 9, 'British Columbia': 10, 'Yukon Territory': 11, 'Northwest Territories': 12, 'Nunavut': 13},
        'fr': {'Terre-Neuve et Labrador': 1, 'Nouvelle-Écosse': 2, 'Île-du-Prince-Édouard': 3, 'Nouveau-Brunswick': 4, 'Québec': 5, 'Ontario': 6, 'Manitoba': 7, 'Saskatchewan': 8, 'Alberta': 9, 'Colombie-Britannique': 10, 'Territoire du Yukon': 11, 'Territoires du Nord-Ouest': 12, 'Nunavut': 13}
    },
    'provider': {
        'en': {'Other': 1, 'Federal': 2, 'Provincial / Territorial': 3, 'Municipal': 4},
        'fr': {'Autre': 1, 'Fédéral': 2, 'Provincial / Territorial': 3, 'Municipal': 4}
    },
    'digitizing_direction_flag': {
        'en': {'Same Direction': 1, 'Opposite Direction': 2, 'Not Applicable': 3},
        'fr': {'Même sens': 1, 'Sens opposé': 2, 'Sans objet': 3}
    },
    'house_number_type': {
        'en': {'Unknown': -1, 'None': 0, 'Actual Located': 1, 'Actual Unlocated': 2, 'Projected': 3, 'Interpolated': 4},
        'fr': {'Inconnu': -1, 'Aucun': 0, 'Localisation réelle': 1, 'Localisation présumée': 2, 'Projeté': 3, 'Interpolé': 4}
    },
    'house_number_structure': {
        'en': {'Unknown': -1, 'None': 0, 'Even': 1, 'Odd': 2, 'Mixed': 3, 'Irregular': 4},
        'fr': {'Inconnu': -1, 'Aucun': 0, 'Numéros pairs': 1, 'Numéros impairs': 2, 'Numéros mixtes': 3, 'Numéros irréguliers': 4}
    },
    'reference_system_indicator': {
        'en': {'Unknown': -1, 'None': 0, 'Civic': 1, 'Lot and Concession': 2, '911 Measured': 3, '911 Civic': 4, 'DLS Townships': 5},
        'fr': {'Inconnu': -1, 'Aucun': 0, 'Civique': 1, 'Lot et concession': 2, 'Mesuré 911': 3, 'Civique 911': 4, 'DLS': 5}
    },
    'blocked_passage_type': {
        'en': {'Unknown': -1, 'Permanently Fixed': 1, 'Removable': 2},
        'fr': {'Inconnu': -1, 'Permanente': 1, 'Amovible': 2}
    },
    'junction_type': {
        'en': {'Intersection': 1, 'Dead End': 2, 'Ferry': 3, 'NatProvTer': 4},
        'fr': {'Intersection': 1, 'Cul-de-sac': 2, 'Transbordement': 3, 'NatProvTer': 4}
    },
    'closing_period': {
        'en': {'Unknown': -1, 'None': 0, 'Summer': 1, 'Winter': 2},
        'fr': {'Inconnu': -1, 'Aucun': 0, 'Été': 1, 'Hiver': 2}
    },
    'functional_roadclass': {
        'en': {'Freeway': 1, 'Expressway / Highway': 2, 'Arterial': 3, 'Collector': 4, 'Local / Street': 5, 'Local / Strata': 6, 'Local / Unknown': 7, 'Alleyway / Lane': 8, 'Ramp': 9, 'Resource / Recreation': 10, 'Rapid Transit': 11, 'Service Lane': 12, 'Winter': 13},
        'fr': {'Autoroute': 1, 'Route express': 2, 'Artère': 3, 'Route collectrice': 4, 'Local / Rue': 5, 'Local / Semi-privé': 6, 'Local / Inconnu': 7, 'Ruelle / Voie': 8, 'Bretelle': 9, "Route d'accès ressources / Site récréatif": 10, 'Réservée transport commun': 11, 'Service': 12, 'Hiver': 13}
    },
    'paved_road_surface_type': {
        'en': {'Unknown': -1, 'None': 0, 'Rigid': 1, 'Flexible': 2, 'Blocks': 3},
        'fr': {'Inconnu': -1, 'Aucun': 0, 'Rigide': 1, 'Souple': 2, 'Pavés': 3}
    },
    'pavement_status': {
        'en': {'Paved': 1, 'Unpaved': 2},
        'fr': {'Revêtue': 1, 'Non revêtue': 2}
    },
    'structure_type': {
        'en': {'None': 0, 'Bridge': 1, 'Bridge covered': 2, 'Bridge moveable': 3, 'Bridge unknown': 4, 'Tunnel': 5, 'Snowshed': 6, 'Dam': 7},
        'fr': {'Aucun': 0, 'Pont': 1, 'Pont couvert': 2, 'Pont mobile': 3, 'Pont inconnu': 4, 'Tunnel': 5, 'Paraneige': 6, 'Barrage': 7}
    },
    'traffic_direction': {
        'en': {'Unknown': -1, 'Both directions': 1, 'Same direction': 2, 'Opposite direction': 3},
        'fr': {'Inconnu': -1, 'Bi-directionel': 1, 'Même direction': 2, 'Direction contraire': 3}
    },
    'unpaved_road_surface_type': {
        'en': {'Unknown': -1, 'None': 0, 'Gravel': 1, 'Dirt': 2},
        'fr': {'Inconnu': -1, 'Aucun': 0, 'Gravier': 1, 'Terre': 2}
    },
    'directional_indicator': {
        'en': {'None': 0, 'North': 1, 'Nord': 2, 'South': 3, 'Sud': 4, 'East': 5, 'Est': 6, 'West': 7, 'Ouest': 8, 'Northwest': 9, 'Nord-ouest': 10, 'Northeast': 11, 'Nord-est': 12, 'Southwest': 13, 'Sud-ouest': 14, 'Southeast': 15, 'Sud-est': 16, 'Central': 17, 'Centre': 18},
        'fr': {'Aucun': 0, 'North': 1, 'Nord': 2, 'South': 3, 'Sud': 4, 'East': 5, 'Est': 6, 'West': 7, 'Ouest': 8, 'Northwest': 9, 'Nord-ouest': 10, 'Northeast': 11, 'Nord-est': 12, 'Southwest': 13, 'Sud-ouest': 14, 'Southeast': 15, 'Sud-est': 16, 'Central': 17, 'Centre': 18}
    },
    'muni_quadrant': {
        'en': {'None': 0, 'South-West': 1, 'South-East': 2, 'North-East': 3, 'North-West': 4},
        'fr': {'Aucun': 0, 'South-West': 1, 'South-East': 2, 'North-East': 3, 'North-West': 4}
    },
    'place_type': {
        'en': ['None', 'Borough / Borough', 'Chartered Community', 'City / Cité', 'City / Ville', 'Community / Communauté', 'County (Municipality) / Comté (Municipalité)', 'Cree Village / Village Cri', 'Crown Colony / Colonie de la couronne', 'District (Municipality) / District (Municipalité)', 'Hamlet / Hameau', 'Improvement District', 'Indian Government District', 'Indian Reserve / Réserve indienne', 'Indian Settlement / Établissement indien', 'Island Municipality', 'Local Government District', 'Lot / Lot', 'Municipal District / District municipal', 'Municipality / Municipalité', 'Naskapi Village / Village Naskapi', "Nisga'a land / Terre Nisga'a", "Nisga'a Village / Village Nisga'a", 'Northern Hamlet / Hameau nordique', 'Northern Town / Ville nordique', 'Northern Village / Village nordique', 'Parish (Municipality) / Paroisse (Municipalité)', 'Parish / Paroisse', 'Region / Région', 'Regional District Electoral Area', 'Regional Municipality / Municipalité régionale', 'Resort Village / Centre de villégiature', 'Rural Community', 'Rural Municipality / Municipalité rurale', 'Settlement / Établissement', 'Special Area', 'Specialized Municipality / Municipalité spécialisée', 'Subdivision of County Municipality', 'Subdivision of Regional District', 'Subdivision of Unorganized', 'Summer Village / Village estival', 'Terre inuite', 'Terres réservées', 'Teslin land / Terre Teslin', 'Town / Ville', 'Township (Municipality) / Canton (Municipalité)', 'Township / Canton', 'United Township (Municipality) / Cantons-unis (Municipalité)', 'Unorganized / Non-organisé', 'Village / Village', 'Without Designation (Municipality) / Sans désignation (Municipalité)'],
        'fr': ['Aucun', 'Borough / Borough', 'Chartered Community', 'City / Cité', 'City / Ville', 'Community / Communauté', 'County (Municipality) / Comté (Municipalité)', 'Cree Village / Village Cri', 'Crown Colony / Colonie de la couronne', 'District (Municipality) / District (Municipalité)', 'Hamlet / Hameau', 'Improvement District', 'Indian Government District', 'Indian Reserve / Réserve indienne', 'Indian Settlement / Établissement indien', 'Island Municipality', 'Local Government District', 'Lot / Lot', 'Municipal District / District municipal', 'Municipality / Municipalité', 'Naskapi Village / Village Naskapi', "Nisga'a land / Terre Nisga'a", "Nisga'a Village / Village Nisga'a", 'Northern Hamlet / Hameau nordique', 'Northern Town / Ville nordique', 'Northern Village / Village nordique', 'Parish (Municipality) / Paroisse (Municipalité)', 'Parish / Paroisse', 'Region / Région', 'Regional District Electoral Area', 'Regional Municipality / Municipalité régionale', 'Resort Village / Centre de villégiature', 'Rural Community', 'Rural Municipality / Municipalité rurale', 'Settlement / Établissement', 'Special Area', 'Specialized Municipality / Municipalité spécialisée', 'Subdivision of County Municipality', 'Subdivision of Regional District', 'Subdivision of Unorganized', 'Summer Village / Village estival', 'Terre inuite', 'Terres réservées', 'Teslin land / Terre Teslin', 'Town / Ville', 'Township (Municipality) / Canton (Municipalité)', 'Township / Canton', 'United Township (Municipality) / Cantons-unis (Municipalité)', 'Unorganized / Non-organisé', 'Village / Village', 'Without Designation (Municipality) / Sans désignation (Municipalité)']
    },
    'street_name_article': {
        'en': ['None', 'à', "à l'", 'à la', 'au', 'aux', 'by the', 'chez', "d'", 'de', "de l'", 'de la', 'des', 'du', "l'", 'la', 'le', 'les', 'of the', 'the'],
        'fr': ['Aucun', 'à', "à l'", 'à la', 'au', 'aux', 'by the', 'chez', "d'", 'de', "de l'", 'de la', 'des', 'du', "l'", 'la', 'le', 'les', 'of the', 'the']
    },
    'street_type': {
        'en': ['None', 'Abbey', 'Access', 'Acres', 'Aire', 'Allée', 'Alley', 'Autoroute', 'Avenue', 'Barrage', 'Bay', 'Beach', 'Bend', 'Bloc', 'Block', 'Boulevard', 'Bourg', 'Brook', 'By-pass', 'Byway', 'Campus', 'Cape', 'Carre', 'Carrefour', 'Centre', 'Cercle', 'Chase', 'Chemin', 'Circle', 'Circuit', 'Close', 'Common', 'Concession', 'Corners', 'Côte', 'Cour', 'Court', 'Cove', 'Crescent', 'Croft', 'Croissant', 'Crossing', 'Crossroads', 'Cul-de-sac', 'Dale', 'Dell', 'Desserte', 'Diversion', 'Downs', 'Drive', 'Droit de passage', 'Échangeur', 'End', 'Esplanade', 'Estates', 'Expressway', 'Extension', 'Farm', 'Field', 'Forest', 'Front', 'Gardens', 'Gate', 'Glade', 'Glen', 'Green', 'Grounds', 'Grove', 'Harbour', 'Haven', 'Heath', 'Heights', 'Highlands', 'Highway', 'Hill', 'Hollow', 'Île', 'Impasse', 'Island', 'Key', 'Knoll', 'Landing', 'Lane', 'Laneway', 'Limits', 'Line', 'Link', 'Lookout', 'Loop', 'Mall', 'Manor', 'Maze', 'Meadow', 'Mews', 'Montée', 'Moor', 'Mount', 'Mountain', 'Orchard', 'Parade', 'Parc', 'Park', 'Parkway', 'Passage', 'Path', 'Pathway', 'Peak', 'Pines', 'Place', 'Plateau', 'Plaza', 'Point', 'Port', 'Private', 'Promenade', 'Quay', 'Rang', 'Range', 'Reach', 'Ridge', 'Right of Way', 'Rise', 'Road', 'Rond Point', 'Route', 'Row', 'Rue', 'Ruelle', 'Ruisseau', 'Run', 'Section', 'Sentier', 'Sideroad', 'Square', 'Street', 'Stroll', 'Subdivision', 'Terrace', 'Terrasse', 'Thicket', 'Towers', 'Townline', 'Trace', 'Trail', 'Trunk', 'Turnabout', 'Vale', 'Via', 'View', 'Village', 'Vista', 'Voie', 'Walk', 'Way', 'Wharf', 'Wood', 'Woods', 'Wynd'],
        'fr': ['Aucun', 'Abbey', 'Access', 'Acres', 'Aire', 'Allée', 'Alley', 'Autoroute', 'Avenue', 'Barrage', 'Bay', 'Beach', 'Bend', 'Bloc', 'Block', 'Boulevard', 'Bourg', 'Brook', 'By-pass', 'Byway', 'Campus', 'Cape', 'Carre', 'Carrefour', 'Centre', 'Cercle', 'Chase', 'Chemin', 'Circle', 'Circuit', 'Close', 'Common', 'Concession', 'Corners', 'Côte', 'Cour', 'Court', 'Cove', 'Crescent', 'Croft', 'Croissant', 'Crossing', 'Crossroads', 'Cul-de-sac', 'Dale', 'Dell', 'Desserte', 'Diversion', 'Downs', 'Drive', 'Droit de passage', 'Échangeur', 'End', 'Esplanade', 'Estates', 'Expressway', 'Extension', 'Farm', 'Field', 'Forest', 'Front', 'Gardens', 'Gate', 'Glade', 'Glen', 'Green', 'Grounds', 'Grove', 'Harbour', 'Haven', 'Heath', 'Heights', 'Highlands', 'Highway', 'Hill', 'Hollow', 'Île', 'Impasse', 'Island', 'Key', 'Knoll', 'Landing', 'Lane', 'Laneway', 'Limits', 'Line', 'Link', 'Lookout', 'Loop', 'Mall', 'Manor', 'Maze', 'Meadow', 'Mews', 'Montée', 'Moor', 'Mount', 'Mountain', 'Orchard', 'Parade', 'Parc', 'Park', 'Parkway', 'Passage', 'Path', 'Pathway', 'Peak', 'Pines', 'Place', 'Plateau', 'Plaza', 'Point', 'Port', 'Private', 'Promenade', 'Quay', 'Rang', 'Range', 'Reach', 'Ridge', 'Right of Way', 'Rise', 'Road', 'Rond Point', 'Route', 'Row', 'Rue', 'Ruelle', 'Ruisseau', 'Run', 'Section', 'Sentier', 'Sideroad', 'Square', 'Street', 'Stroll', 'Subdivision', 'Terrace', 'Terrasse', 'Thicket', 'Towers', 'Townline', 'Trace', 'Trail', 'Trunk', 'Turnabout', 'Vale', 'Via', 'View', 'Village', 'Vista', 'Voie', 'Walk', 'Way', 'Wharf', 'Wood', 'Woods', 'Wynd']
    },
    'toll_point_type': {
        'en': {'Unknown': -1, 'Physical Toll Booth': 1, 'Virtual Toll Booth': 2, 'Hybrid': 3},
        'fr': {'Inconnu': -1, 'Poste de péage': 1, 'Poste de péage virtuel': 2, 'Hybride': 3}
    }
}

# Schema information for all the fields across the dataset
# {
#     field: {
#         format: {
#             en: name,
#             fr: name
#         },
#         width: value,
#         type: value,
#         [domains: value] - optional
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
        'type': ogr.OFTString,
        'domains': domains['dataset_name']
    },
    'acqtech': {
        'gpkg': {'en': 'ACQTECH', 'fr': 'TECHACQ'},
        'shp': {'en': 'ACQTECH', 'fr': 'TECHACQ'},
        'gml': {'en': 'acquisitionTechnique', 'fr': 'techniqueAcquisition'},
        'kml': {'en': None, 'fr': None},
        'width': 23,
        'type': ogr.OFTString,
        'domains': domains['acquisition_technique']
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
        'type': ogr.OFTString,
        'domains': domains['metadata_coverage']
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
        'type': ogr.OFTString,
        'domains': domains['provider']
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
        'type': ogr.OFTString,
        'domains': domains['digitizing_direction_flag']
    },
    'r_digdirfg': {
        'gpkg': {'en': 'R_DIGDIRFG', 'fr': 'SENSNUM_D'},
        'shp': {'en': 'R_DIGDIRFG', 'fr': 'SENSNUM_D'},
        'gml': {'en': 'right_DigitizingDirectionFlag', 'fr': 'sensNumerisation_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 18,
        'type': ogr.OFTString,
        'domains': domains['digitizing_direction_flag']
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
        'type': ogr.OFTString,
        'domains': domains['house_number_type']
    },
    'r_hnumtypf': {
        'gpkg': {'en': 'R_HNUMTYPF', 'fr': 'TYPENUMP_D'},
        'shp': {'en': 'R_HNUMTYPF', 'fr': 'TYPENUMP_D'},
        'gml': {'en': 'right_FirstHouseNumberType', 'fr': 'typeNumPremiereMaison_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 16,
        'type': ogr.OFTString,
        'domains': domains['house_number_type']
    },
    'l_hnumstr': {
        'gpkg': {'en': 'L_HNUMSTR', 'fr': 'STRUNUM_G'},
        'shp': {'en': 'L_HNUMSTR', 'fr': 'STRUNUM_G'},
        'gml': {'en': 'left_HouseNumberStructure', 'fr': 'structureNumMaison_Gauche'},
        'kml': {'en': None, 'fr': None},
        'width': 9,
        'type': ogr.OFTString,
        'domains': domains['house_number_structure']
    },
    'r_hnumstr': {
        'gpkg': {'en': 'R_HNUMSTR', 'fr': 'STRUNUM_D'},
        'shp': {'en': 'R_HNUMSTR', 'fr': 'STRUNUM_D'},
        'gml': {'en': 'right_HouseNumberStructure', 'fr': 'structureNumMaison_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 9,
        'type': ogr.OFTString,
        'domains': domains['house_number_structure']
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
        'type': ogr.OFTString,
        'domains': domains['house_number_type']
    },
    'r_hnumtypl': {
        'gpkg': {'en': 'R_HNUMTYPL', 'fr': 'TYPENUMD_D'},
        'shp': {'en': 'R_HNUMTYPL', 'fr': 'TYPENUMD_D'},
        'gml': {'en': 'right_LastHouseNumberType', 'fr': 'typeNumDerniereMaison_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 16,
        'type': ogr.OFTString,
        'domains': domains['house_number_type']
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
        'type': ogr.OFTString,
        'domains': domains['reference_system_indicator']
    },
    'r_rfsysind': {
        'gpkg': {'en': 'R_RFSYSIND', 'fr': 'SYSREF_D'},
        'shp': {'en': 'R_RFSYSIND', 'fr': 'SYSREF_D'},
        'gml': {'en': 'right_ReferenceSystemIndicator', 'fr': 'indicSystemeReference_Droite'},
        'kml': {'en': None, 'fr': None},
        'width': 18,
        'type': ogr.OFTString,
        'domains': domains['reference_system_indicator']
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
        'type': ogr.OFTString,
        'domains': domains['blocked_passage_type']
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
        'type': ogr.OFTString,
        'domains': domains['closing_period']
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
        'type': ogr.OFTString,
        'domains': domains['functional_roadclass']
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
        'type': ogr.OFTString,
        'domains': domains['junction_type']
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
        'type': ogr.OFTString,
        'domains': domains['paved_road_surface_type']
    },
    'pavstatus': {
        'gpkg': {'en': 'PAVSTATUS', 'fr': 'ETATREV'},
        'shp': {'en': 'PAVSTATUS', 'fr': 'ETATREV'},
        'gml': {'en': 'pavementStatus', 'fr': 'etatRevetement'},
        'kml': {'en': None, 'fr': None},
        'width': 7,
        'type': ogr.OFTString,
        'domains': domains['pavement_status']
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
        'type': ogr.OFTString,
        'domains': domains['structure_type']
    },
    'trafficdir': {
        'gpkg': {'en': 'TRAFFICDIR', 'fr': 'SENSCIRCUL'},
        'shp': {'en': 'TRAFFICDIR', 'fr': 'SENSCIRCUL'},
        'gml': {'en': 'trafficDirection', 'fr': 'sensCirculation'},
        'kml': {'en': None, 'fr': None},
        'width': 18,
        'type': ogr.OFTString,
        'domains': domains['traffic_direction']
    },
    'unpavsurf': {
        'gpkg': {'en': 'UNPAVSURF', 'fr': 'TYPENONREV'},
        'shp': {'en': 'UNPAVSURF', 'fr': 'TYPENONREV'},
        'gml': {'en': 'unpavedRoadSurfaceType', 'fr': 'typeChausseeNonRevetue'},
        'kml': {'en': None, 'fr': None},
        'width': 7,
        'type': ogr.OFTString,
        'domains': domains['unpaved_road_surface_type']
    },
    'dirprefix': {
        'gpkg': {'en': 'DIRPREFIX', 'fr': 'PREDIR'},
        'shp': {'en': 'DIRPREFIX', 'fr': 'PREDIR'},
        'gml': {'en': 'directionalPrefix', 'fr': 'prefixeDirection'},
        'kml': {'en': None, 'fr': None},
        'width': 10,
        'type': ogr.OFTString,
        'domains': domains['directional_indicator']
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
        'type': ogr.OFTString,
        'domains': domains['muni_quadrant']
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
        'type': ogr.OFTString,
        'domains': domains['place_type']
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
        'type': ogr.OFTString,
        'domains': domains['street_name_article']
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
        'type': ogr.OFTString,
        'domains': domains['street_type']
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

_table_names = {
    'addrange': {
        'shp': {'en': 'ADDRANGE', 'fr': 'INTERVADR'},
        'gpkg': {'en': 'ADDRANGE', 'fr': 'INTERVADR'},
        'gml': {'en': 'AddressRange', 'fr': 'IntervalleAddresse'},
    },
    'altnamlink': {
        'shp': {'en': '', 'fr': ''},
        'gpkg': {'en': 'ALTNAMELINK', 'fr': 'LIENNOFF'},
        'gml': {'en': 'AlternateNameLink', 'fr': 'LieuNomNonOfficiel'},
    },
    'blkpassage': {
        'shp': {'en': 'BLKPASSAGE', 'fr': 'PASSAGEOBS'},
        'gpkg': {'en': 'BLKPASSAGE', 'fr': 'PASSAGEOBS'},
        'gml': {'en': 'BlockedPassage', 'fr': 'PassageObstrue'},
    },
    'ferryseg': {
        'shp': {'en': 'FERRYSEG', 'fr': 'SLIAISONTR'},
        'gpkg': {'en': 'FERRYSEG', 'fr': 'SLIAISONTR'},
        'gml': {'en': 'FerrySegment', 'fr': 'SegmentLiaisonTransbordeur'},
    },
    'junction': {
        'shp': {'en': 'JUNCTION', 'fr': 'JONCTION'},
        'gpkg': {'en': 'JUNCTION', 'fr': 'JONCTION'},
        'gml': {'en': 'Junction', 'fr': 'Jonction'},
    },
    'roadseg': {
        'shp': {'en': 'ROADSEG', 'fr': 'SEGMROUT'},
        'gpkg': {'en': 'ROADSEG', 'fr': 'SEGMROUT'},
        'gml': {'en': 'RoadSegment', 'fr': 'SegmentRoutier'},
    },
    'strplaname': {
        'shp': {'en': 'STRPLANAME', 'fr': 'NOMRUELIEU'},
        'gpkg': {'en': 'STRPLANAME', 'fr': 'NOMRUELIEU'},
        'gml': {'en': 'StreetPlaceName', 'fr': 'NomRueLieu'},
    },
    'tollpoint': {
        'shp': {'en': 'TOLLPOINT', 'fr': 'POSTEPEAGE'},
        'gpkg': {'en': 'TOLLPOINT', 'fr': 'POSTEPEAGE'},
        'gml': {'en': 'TollPoint', 'fr': 'PostePeage'},
    },
}

# Table definitions that can exist in each dataset.
class BaseTable:
    """Superclass to layers within a dataset."""
    def __init__(self, key: str):
        logger.debug("BaseTable initialization started")

        logger.debug("Initializing table %s", key)
        self.key = key

        # Common fields
        self.fields = ['nid', 'credate', 'revdate', 'datasetnam', 'acqtech', 'specvers']
        logger.debug("Fields decalred: %s", self.fields)

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

        logger.debug("BaseTable initialization complete")
    
    def __repr__(self):
        """Print the class key and shape type when printing to user readable output."""
        return f'{self.key} <{ogr.GeometryTypeToName(self.shape_type)}>'

    def get_table_name(self, file_format: str, lang: str):
        """Get the table name for a given format specification."""
        table_name_defn = _table_names.get(self.key)

        # make sure a name exists for the requested format
        if file_format.lower() not in table_name_defn:
            raise ValueError(f'Table format not implemented for {file_format}')

        table_names_for_format = table_name_defn.get(file_format.lower())
        table_name = table_names_for_format.get(lang)
        return table_name
    
    def field_has_domain(self, field_name: str):
        """Check if a given field has a domain applied to it."""
        field_name = field_name.lower()

        return 'domains' in schema.get(field_name)
    
    def get_field_domain(self, field_name: str, lang: str = 'en') -> dict:
        """Return the domain for a given field."""
        field_name = field_name.lower()

        if not self.field_has_domain(field_name):
            raise ValueError(f'{field_name} does not have a domain')

        field_domain_by_lang = schema.get(field_name).get('domains')
        return field_domain_by_lang.get(lang)
    
    def get_field_names(self):
        """Return the list of field names defined on this table."""
        return self.fields

class AddressRangeTable(BaseTable):
    """Definition of the address range table."""

    def __init__(self):
        logger.debug("%s initialization started", self.__class__.__name__)
        super().__init__('addrange')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'l_altnamnid', 'r_altnamnid', 'l_digdirfg', 
                            'r_digdirfg', 'l_hnumf', 'r_hnumf', 'l_hnumsuff', 'r_hnumsuff', 'l_hnumtypf',
                            'r_hnumtypf', 'l_hnumstr', 'r_hnumstr', 'l_hnuml', 'r_hnuml', 'l_hnumsufl',
                            'r_hnumsufl', 'l_hnumtypl', 'r_hnumtypl', 'l_offnanid', 'r_offnanid', 'l_rfsysind',
                            'r_rfsysind'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

class AlternateNameLinkTable(BaseTable):
    """Definition of the Alternate Name Link table."""
    def __init__(self):
        super().__init__('altnamlink')

        self.fields.extend(['strnamenid'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

class BlockedPassageTable(BaseTable):
    """Definition of the Blocked Passage table."""
    def __init__(self):
        super().__init__('blkpassage')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'blkpassty', 'roadnid'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbPoint
        logger.debug("Shape type: %s", self.shape_type)

class FerrySegmentTable(BaseTable):
    """Definition of the Ferry Segment table."""
    def __init__(self):
        super().__init__('ferryseg')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'closing', 'ferrysegid', 'roadclass',
                            'rtename1en', 'rtename2en', 'rtename3en', 'rtename4en',
                            'rtename1fr', 'rtename2fr', 'rtename3fr', 'rtename4fr',
                            'rtnumber1', 'rtnumber2', 'rtnumber3', 'rtnumber4', 'rtnumber5'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbLineString
        logger.debug("Shape type: %s", self.shape_type)

class JunctionTable(BaseTable):
    """Definition of the Junction table."""
    def __init__(self):
        super().__init__('junction')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'exitnbr', 'junctype'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbPoint
        logger.debug("Shape type: %s", self.shape_type)

class RoadSegmentTable(BaseTable):
    """Definition of the road segment table."""
    def __init__(self):
        super().__init__('roadseg')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'l_adddirfg', 'r_adddirfg', 'adrangenid',
                            'closing', 'exitnbr', 'l_hnumf', 'r_hnumf', 'roadclass', 'l_hnuml', 'r_hnuml',
                            'nbrlanes', 'l_placenam', 'r_placenam', 'l_stname_c', 'r_stname_c', 'pavsurf',
                            'pavstatus', 'roadjuris', 'roadsegid',
                            'rtename1en', 'rtename2en', 'rtename3en', 'rtename4en',
                            'rtename1fr', 'rtename2fr', 'rtename3fr', 'rtename4fr',
                            'rtnumber1', 'rtnumber2', 'rtnumber3', 'rtnumber4', 'rtnumber5',
                            'speed', 'strunameen', 'strunamefr', 'structid', 'structtype', 'trafficdir', 'unpavsurf'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbLineString
        logger.debug("Shape type: %s", self.shape_type)

class StreetPlaceNameTable(BaseTable):
    """Definition of the street and place name table."""
    def __init__(self):
        super().__init__('strplaname')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'dirprefix', 'dirsuffix', 'muniquad', 'placename',
                            'placetype', 'province', 'starticle', 'namebody', 'strtypre', 'strtysuf'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

class TollPointTable(BaseTable):
    """Definition of the toll point table."""
    def __init__(self):
        super().__init__('tollpoint')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'roadnid', 'tollpttype'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbPoint
        logger.debug("Shape type: %s", self.shape_type)

# Map table short names to their matching class
class_map = {
    'addrange': AddressRangeTable(),
    'altnamlink': AlternateNameLinkTable(),
    'blkpassage': BlockedPassageTable(),
    'ferryseg': FerrySegmentTable(),
    'junction': JunctionTable(),
    'roadseg': RoadSegmentTable(),
    'strplaname': StreetPlaceNameTable(),
    'tollpoint': TollPointTable()
}
