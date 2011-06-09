#!/usr/bin/python

#
# Assemble tiles into a larger image
#

import Image
import urllib2
from cStringIO import StringIO
import os

class DataInfo:
    tilesize = 256
    rows = 468
    cols = 529
    xMax = 5200 * 23
    yMax = 5200 * 26
    
    #root = 'http://openconnectomeproject.org/data/brain' # needs to be more flexible
    root = '/data'

    def __init__(self):
        pass

    #def fullWidthInPixels(self):
    #    return self.cols * self.imagewidth

    #def fullHeightInPixels(self):
    #    return self.cols * self.imagewidth

    def getFileLocation(self, scale, slice, row, col):
        return "{0}/{1}/{2}/{3}_{4}.png".format(self.root, scale, slice, col, row) # ARG! need to switch format to row_col

def main(root='brain', slice=2917, scale=0, cols=1, rows=1, slices=1, row=1, col=1): 

    data = DataInfo()
    
    data.root = os.path.join(data.root, root)
    
    for tslice in xrange(slice, slice + slices):
        img = Image.new("L", (256 * rows, 256 * cols))
        for trow in xrange(rows):
            for tcol in xrange(cols):

                filename = data.getFileLocation(scale, tslice, row + trow, col + tcol)
                #tURL = urllib2.urlopen(filename)    # grab image from remote host
                #t = Image.open(StringIO(tURL.read())) 
                t = Image.open(filename) 
                img.paste(t, (256 * trow, 256 * tcol))
        
        return img
   
if __name__ == "__main__":
    main()