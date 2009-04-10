import os
import re
import gtk
import sys
import urllib
import openanything
import fileUtils

from time import time
from mapConst import *
from threading import Lock
from gobject import TYPE_STRING

class GoogleMaps:

    # coord = (lat, lng, zoom_level)
    map_server_query=["","h","p"]

    @staticmethod
    def set_zoom(intZoom):
        if (MAP_MIN_ZOOM_LEVEL <= intZoom <= MAP_MAX_ZOOM_LEVEL):
            return intZoom
        else:
            return 10

    def layer_url_template(self, layer, online):
        if layer not in self.known_layers:
            self.version_string=None
            if not online:
                return None
            oa = openanything.fetch(
                'http://maps.google.com/maps?t='+self.map_server_query[layer])
            if oa['status'] != 200:
                print "Trying to fetch http://maps.google.com/maps but failed"
                return None
            html=oa['data']
            p=re.compile(
                'http://([a-z]{2,3})[0-9].google.com/([a-z]+)[?/]v=([a-z0-9.]+)&')
            m=p.search(html)
            if not m:
                print "Cannot parse result"
                return None
            self.known_layers[layer] = (
                'http://%s%%d.google.com/%s/v=%s&hl=en&x=%%i&y=%%i&zoom=%%i' 
                % tuple(m.groups()))
            print "URL pattern for layer %i: %s" % (layer,self.known_layers[layer])

        return self.known_layers[layer]

    def get_png_file(self, coord, layer, filename, online, force_update):
        # remove tile only when online
        if (os.path.isfile(filename) and force_update and online):
            # Don't remove old tile unless it is downloaded more
            # than 24 hours ago (24h * 3600s) = 86400
            if (int(time() - os.path.getmtime(filename)) > 86400):
                os.remove(filename)

        if os.path.isfile(filename):
            return True
        if not online:
            return False

        t=self.layer_url_template(layer,online)
        if not t:
            return False

        href = t % (
                self.mt_counter,
                coord[0], coord[1], coord[2])
        self.mt_counter += 1
        self.mt_counter = self.mt_counter % NR_MTS
        try:
            print 'downloading:', href
            oa = openanything.fetch(href)
            if oa['status']==200:
                file = open( filename, 'wb' )
                file.write( oa['data'] )
                file.close()
                return True
        except KeyboardInterrupt:
            raise
        except:
            print '\tdownload failed -', sys.exc_info()[0]
        return False

    def read_locations(self):
        self.locations = fileUtils.read_file('location', self.locationpath)

    def write_locations(self):
        fileUtils.write_file('location', self.locationpath, self.locations)

    def __init__(self, configpath=None):
        configpath = os.path.expanduser(configpath or "~/.googlemaps")
        self.lock = Lock()
        self.mt_counter=0
        self.configpath = fileUtils.check_dir(configpath)
        self.locationpath = os.path.join(self.configpath, 'locations')
        self.known_layers = {}
        self.locations = {}

        if (os.path.exists(self.locationpath)):
            self.read_locations()
        else:
            self.write_locations()

    def get_locations(self):
        return self.locations

    def search_location(self, location):
        print 'downloading the following location:', location
        try:
            oa = openanything.fetch( 'http://maps.google.com/maps?q=' +
                urllib.quote_plus(location) )
        except Exception:
            return 'error=Can not connect to http://maps.google.com'
        if oa['status']!=200:
            return 'error=Can not connect to http://maps.google.com'

        html = oa['data']
        # List of patterns to look for the location name
        paList = ['laddr:"([^"]+)"',
                  'daddr:"([^"]+)"']
        for srtPattern in paList:
            p = re.compile(srtPattern)
            m = p.search(html)
            if m: break
        if m:
            location = m.group(1)
        else:
            m = p.search(html)
            return 'error=Location %s not found' % location

        # List of patterns to look for the latitude & longitude
        paList = ['center:{lat:([0-9.-]+),lng:([0-9.-]+)}.*zoom:([0-9.-]+)',
                  'markers:.*lat:([0-9.-]+),lng:([0-9.-]+).*laddr:',
                  'dtlsUrl:.*x26sll=([0-9.-]+),([0-9.-]+).*x26sspn']

        for srtPattern in paList:
            p = re.compile(srtPattern)
            m = p.search(html)
            if m: break

        if m:
            lat, lng = float(m.group(1)), float(m.group(2))
            zoom = 10
            if m.group(0).find('zoom:') != -1:
                zoom = self.set_zoom(MAP_MAX_ZOOM_LEVEL - int(m.group(3)))
            else:
                p = re.compile('center:.*zoom:([0-9.-]+).*mapType:')
                m = p.search(html)
                if m:
                    zoom = self.set_zoom(MAP_MAX_ZOOM_LEVEL - int(m.group(1)))
            location = unicode(location, errors='ignore')
            self.locations[location] = (lat, lng, zoom)
            self.write_locations()
            return location
        else:
            return 'error=Unable to get latitude and longitude of %s ' % location


    def coord_to_path(self, coord, layer):
        self.lock.acquire()
        ## at most 1024 files in one dir
        ## We only have 2 levels for one axis
        path = fileUtils.check_dir(self.configpath, LAYER_DIRS[layer])
        path = fileUtils.check_dir(path, '%d' % coord[2])
        path = fileUtils.check_dir(path, "%d" % (coord[0] / 1024))
        path = fileUtils.check_dir(path, "%d" % (coord[0] % 1024))
        path = fileUtils.check_dir(path, "%d" % (coord[1] / 1024))
        self.lock.release()
        return os.path.join(path, "%d.png" % (coord[1] % 1024))

    def get_file(self, coord, layer, online, force_update):
        if (MAP_MIN_ZOOM_LEVEL <= coord[2] <= MAP_MAX_ZOOM_LEVEL):
            world_tiles = 2 ** (MAP_MAX_ZOOM_LEVEL - coord[2])
            if (coord[0] > world_tiles) or (coord[1] > world_tiles):
                return None
            ## Tiles dir structure
            filename = self.coord_to_path(coord, layer)
            # print "Coord to path: %s" % filename
            if (self.get_png_file(coord, layer, filename, online, force_update)):
                return filename
        return None

    def get_tile_pixbuf(self, coord, layer, online, force_update):
        w = gtk.Image()
        # print ("get_tile_pixbuf: zl: %d, coord: %d, %d") % (coord)
        filename = self.get_file(coord, online, force_update)
        if (filename == None):
            filename = 'missing.png'
            w.set_from_file('missing.png')
        else:
            w.set_from_file(filename)

        try:
            return w.get_pixbuf()
        except ValueError:
            print "File corrupted: %s" % filename
            os.remove(filename)
            w.set_from_file('missing.png')
            return w.get_pixbuf()

    def completion_model(self, strAppend=''):
        store = gtk.ListStore(TYPE_STRING)
        for str in sorted(self.locations.keys()):
            iter = store.append()
            store.set(iter, 0, str + strAppend)
        return store