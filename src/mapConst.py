## @package src.mapConst
# Place to keep all constants

NAME = "GMapCatcher"
VERSION = "0.6.0.0"
VERSION_NAME = ""
WEB_ADDRESS = "http://code.google.com/p/gmapcatcher/"

GOOGLE = 0
OSM = 1
CLOUDMADE = 2
YAHOO = 3
INFO_FREEWAY = 4
OPENCYCLEMAP = 5
GOOGLE_MAKER = 6
VIRTUAL_EARTH = 7
MAP_SERVERS = ["Google", "OpenStreetMap", "CloudMade", "Yahoo",
               "InformationFreeway", "OpenCycleMap", "Google Map Maker",
               "Virtual Earth"]

MAP_MAX_ZOOM_LEVEL = 17
MAP_MIN_ZOOM_LEVEL = -2
TILES_WIDTH = 256
TILES_HEIGHT = 256
NR_MTS = 4
SEPARATOR = "\t"
TOOLS_MENU = ["Settings", "Edit locations", "Edit markers",
              "Change Theme", "GPS Options"]

ZOOM_IN = 0
ZOOM_OUT = 1
CENTER_MAP = 2
RESET = 3
BATCH_DOWN = 5
EXPORT_MAP = 6
ADD_MARKER = 7
DA_MENU = ["Zoom In", "Zoom Out", "Center map here",
        "Reset", "", "Batch Download", "Export Map", "Add Marker"]

LAYER_MAP = 0
LAYER_SATELLITE = 1
LAYER_TERRAIN = 2
LAYER_NAMES = ["Map", "Satellite", "Terrain"]
LAYER_DIRS = ["tiles", "sat_tiles", "ter_tiles"]

GPS_IMG_SIZE = (48, 48)

GPS_DISABLED = 0
GPS_MARKER = 1
GPS_CENTER = 2
GPS_ON_SCREEN = 3
GPS_NAMES = ["GPS Disabled", "GPS Marker", "GPS Center", "GPS on Screen"]

SECTION_INIT  = 'init'
R_EARTH = 6371.
USER_PATH = "~"
TILES_PATH = ".googlemaps"
DEFAULT_PATH = USER_PATH + "/" + TILES_PATH