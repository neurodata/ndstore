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
  possible errors to catch:
	request file too large
"""

import web
import assembletiles
from cStringIO import StringIO
import math

urls = ('/(.*)/(.*)/(.*)/(.*)', 'Slice') # todo: better regex

class Slice:
	def GET(self, scale=0, slice=0, startCoor=[0, 0], endCoor=[1, 1]):
		try:
			scale = int(scale)
			slice = int(slice)
		
			startCoor = [int(s) for s in startCoor.split(',')] # or float? convert to 2x2?
			endCoor = [int(s) for s in endCoor.split(',')]
			
			# translate pixel coordinate representation to tile locations
			tileData = assembletiles.DataInfo()
			tileSize = tileData.tilesize * 2 ** scale

			startTile = [int(math.ceil(s / tileSize)) for s in startCoor]
			endTile = [int(math.ceil(s / tileSize)) for s in endCoor]
		
			rows = endTile[0] - startTile[0] + 1
			cols = endTile[1] - startTile[1] + 1  
		
			#rowMax = int(math.ceil(tileData.xMax/tileSize)) # todo: enforce error if > max
			#colMax = int(math.ceil(tileData.yMax/tileSize))
		
			# get tiles captured by requested rectangle
			img = assembletiles.main(
									slice=slice,
									scale=scale,
									row=startTile[0],
									col=startTile[1],
									rows=rows,
									cols=cols
									)

			# crop img to exactly fit requested rectangle userBox
			#   startCoor = upper left corner
			#   endCoor = lower right corner
			#   Image.crop also places origin at upper left corner
			left = startCoor[0] - startTile[0] * tileSize
			right = endCoor[0] - startTile[0] * tileSize
			upper = startCoor[1] - startTile[1] * tileSize
			lower = endCoor[1] - startTile[1] * tileSize
			userBox = tuple([s / (2 ** scale) for s in [left, upper, right, lower]])
			img = img.crop(userBox)
			
			# todo: serve img (8 gig limit)
			ext = 'png'
			temp = StringIO()
			img.save(temp, ext, optimize=1)
			web.header('Content-Type', 'image/%s' % ext)
			temp.seek(0)
			return temp.read()
			# f.close()

		# todo: need more testing to be sure that these are 
		# the only errors per exception type, i.e. perhaps 
		# should make own Error classes
		except ValueError:
			return "Could not convert input to an integer"
		except IndexError:
			return ".../scale/zlevel/x1,y1/x2,y2 input format required" 
			# might want to make format string a variable
		except MemoryError:
			return '\n'.join(["x1,y2 should be the upper left coordinate",
			"x2,y2 should be the lower right coordiate",
			"coordinate system origin = upper left corner"])
		except IOError:
			return "Requested image range out of bounds"

if __name__ == "__main__":
	web.config.debug = False
	web.application(urls, globals()).run()
	
