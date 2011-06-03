#!/usr/bin/python

#
# Serve user requested slice via REST interface
#   x1,y1 = upper left corner
#   x2,y2 = lower left corner
#   coordinate system origin = upper left corner
#   usage: http://host/root/scale/slicelevel/x1,y1/x2,y2
#   ex: http://host/brain/0/2917/35082,25550/35682,25680
#
"""
todo: 
  maybe build up API
  beware of over- or strange-coupling with assembletiles
"""

import web
import assembletiles
from cStringIO import StringIO
import math
import os
#import time

urls = ('/(.*)/(.*)/(.*)/(.*)/(.*)', 'Slice') # todo: better regex
requestLimit = 1000000000

class Slice:
    def GET(self, root='', scale=0, slice=0, startCoor=[0, 0], endCoor=[1, 1]):
        try:
            #ctime = time.time()
            scale = int(scale)
            slice = int(slice)
            
            # Translate pixel coordinate representation to tile locations
            tileData = assembletiles.DataInfo()
            scaleFactor = 2 ** scale
            tileSize = tileData.tilesize
            
            startCoor = [int(math.floor(float(s) / scaleFactor)) for s in startCoor.split(',')]
            endCoor = [int(math.ceil(float(s) / scaleFactor)) for s in endCoor.split(',')]
            
            startCoor.sort()
            endCoor.sort()
            
            startTile = [s / tileSize for s in startCoor]
            endTile = [s / tileSize for s in endCoor]  
            
            rows = endTile[0] - startTile[0] + 1
            cols = endTile[1] - startTile[1] + 1
            
            # Get tiles captured by requested rectangle
            img = assembletiles.main(
                                     root=root,
                                     slice=slice,
                                     scale=scale,
                                     row=startTile[0],
                                     col=startTile[1],
                                     rows=rows,
                                     cols=cols
                                     )
            
            # Crop img to exactly fit requested rectangle userBox
            #   startCoor = upper left corner
            #   endCoor = lower right corner
            #   Image.crop also places origin at upper left corner
            left = startCoor[0] - startTile[0] * tileSize
            upper = startCoor[1] - startTile[1] * tileSize
            right = endCoor[0] - startTile[0] * tileSize
            lower = endCoor[1] - startTile[1] * tileSize
            userBox = left, upper, right, lower
            #return time.time() - ctime
            img = img.crop(userBox)
            
            # Serve img (1 gig limit)
            ext = 'png'
            temp = StringIO()
            img.save(temp, ext, optimize=1)
            web.header('Content-Type', 'image/%s' % ext)
            temp.seek(0, os.SEEK_END)
             
            if (int(temp.tell()) > requestLimit): # perhaps enforcing request limit earlier would be more helpful yes?
                raise RequestEntityTooLarge()
            
            temp.seek(0)
            return temp.read()
            # temp.close()
            
        except IOError:
            raise RangeNotSatisfiable() # Input range out of bounds
        except SystemError:
            raise RangeNotSatisfiable() # Input range out of bounds
        except MemoryError:
            raise RangeNotSatisfiable() # Coordinates did not satisfy x1 < x2, y1 < y2
        except OverflowError:
            raise RangeNotSatisfiable() # Input integer too large for float conversion
        except ValueError:
            raise BadRequest() # Input contained non-integers
        except IndexError:
            raise BadRequest() # Input not formatted correctly

# Error subclasses
class BadRequest(web.HTTPError):
    def __init__(self):
        status = '400 Bad Request'
        headers = {'Content-Type': 'text/html'}
        data = '<h1>400 Bad Request</h1>'
        web.HTTPError.__init__(self, status, headers, data)

class RangeNotSatisfiable(web.HTTPError):
    def __init__(self):
        status = '416 Requested Range Not Satisfiable'
        headers = {'Content-Type': 'text/html'}
        data = '<h1>416 Requested Range Not Satisfiable</h1>'
        web.HTTPError.__init__(self, status, headers, data)

class RequestEntityTooLarge(web.HTTPError):
    def __init__(self):
        status = '413 Request Entity Too Large'
        headers = {'Content-Type': 'text/html'}
        data = '<h1>413 Request Entity Too Large</h1>'
        web.HTTPError.__init__(self, status, headers, data)

if __name__ == "__main__":
	web.config.debug = True
	web.application(urls, globals()).run()