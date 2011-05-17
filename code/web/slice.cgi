#!/usr/bin/python
#
# Serve user requested slice via REST interface
#  x1,y1 = upper left corner
#  x2,y2 = lower left corner
#  coordinate system origin = upper left corner
#  usage: http://host/scale/slicelevel/x1,y1/x2,y2
#  ex: http://host/0/2917/35082,25550/35682,25680
#

import web
import assembletiles
#import zipfile
from cStringIO import StringIO
import math
import os

urls = ('/(.*)/(.*)/(.*)/(.*)','Slice') # todo: better regex
#app = web.application(urls,globals())

# todo: restructure to get some semblance of security
# maybe build up API
# beware of over- or strange-coupling with assembletiles

class Slice:
	def GET(self,scale=0,slice=0,startCoor=[0,0],endCoor=[1,1]):
		scale = int(scale)
		slice = int(slice)
		
		startCoor = [int(s) for s in startCoor.split(',')] # or float? convert to 2x2?
		endCoor = [int(s) for s in endCoor.split(',')]
		
		# translate pixel coordinate representation to tile locations
		tileData = assembletiles.DataInfo()
		tileSize = tileData.tilesize*2**scale

		startTile = [int(math.ceil(s/tileSize)) for s in startCoor]
		endTile = [int(math.ceil(s/tileSize)) for s in endCoor]
		
		rows = endTile[0]-startTile[0] + 1  
		cols = endTile[1]-startTile[1] + 1  
		
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
		left = startCoor[0]-startTile[0]*tileSize
		right = endCoor[0]-startTile[0]*tileSize
		upper = startCoor[1]-startTile[1]*tileSize
		lower = endCoor[1]-startTile[1]*tileSize
		userBox = tuple([s/(2**scale) for s in [left, upper, right, lower]])

		img = img.crop(userBox)
		
		# todo: serve img (8 gig limit)
		try:
			ext = 'png'
			f = StringIO()
			img.save(f,ext,optimize=1)
			web.header('Content-Type','image/%s'%ext)
			f.seek(0)
			return f.read()
			# f.close()
			
		except ValueError:
			return "File to large"

if __name__ == "__main__":
	web.config.debug = True
	web.application(urls, globals()).run()
	#app.run() 
