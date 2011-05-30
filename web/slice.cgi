#!/usr/bin/python

#
# Serve user requested slice via REST interface
#   x1,y1 = upper left corner
#   x2,y2 = lower left corner
#   coordinate system origin = upper left corner
#   usage: http://host/scale/slicelevel/x1,y1/x2,y2
#   ex: http://host/0/2917/35082,25550/35682,25680
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

urls = ('/(.*)/(.*)/(.*)/(.*)','Slice') # todo: better regex
requestLimit = 8000000000

class Slice:
	def GET(self,scale=0,slice=0,startCoor=[0,0],endCoor=[1,1]):
		try:
			scale = int(scale)
			slice = int(slice)
		
			startCoor = [int(s) for s in startCoor.split(',')] # or float? convert to 2x2?
			endCoor = [int(s) for s in endCoor.split(',')]
			
			# Translate pixel coordinate representation to tile locations
			tileData = assembletiles.DataInfo()
			tileSize = tileData.tilesize * 2 ** scale

			startTile = [int(math.ceil(s / tileSize)) for s in startCoor]
			endTile = [int(math.ceil(s / tileSize)) for s in endCoor]
		
			rows = endTile[0] - startTile[0] + 1
			cols = endTile[1] - startTile[1] + 1  
		
			#rowMax = int(math.ceil(tileData.xMax/tileSize)) # todo: enforce error if > max
			#colMax = int(math.ceil(tileData.yMax/tileSize))
		
			# Get tiles captured by requested rectangle
			img = assembletiles.main(
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
			right = endCoor[0] - startTile[0] * tileSize
			upper = startCoor[1] - startTile[1] * tileSize
			lower = endCoor[1] - startTile[1] * tileSize
			userBox = tuple([s / (2 ** scale) for s in [left, upper, right, lower]])
			img = img.crop(userBox)
			
			# Serve img (8 gig limit)
			ext = 'png'
			temp = StringIO()
			img.save(temp, ext, optimize=1)
			web.header('Content-Type', 'image/%s' % ext)

			temp.seek(0,os.SEEK_END)
			if (int(temp.tell()) > requestLimit): # perhaps enforcing request limit earlier would be more helpful yes?
				raise RequestEntityTooLarge()

			temp.seek(0)
			return temp.read()
			# f.close()

		# todo: need more testing to be sure that these are 
		# the only errors per exception type, i.e. perhaps 
		# should make own Error classes
		except IndexError:
			raise BadRequest() # Input not formatted correctly
		except ValueError:
			raise BadRequest() # Input contained non-integers 
		except IOError:
			raise RangeNotSatisfiable() # Input range out of bounds
		except MemoryError:
			raise RangeNotSatisfiable() # Coordinates did not satisfy x1 < x2, y1 < y2
        	except SystemError:
            		raise RangeNotSatisfiable() # Input range out of bounds

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