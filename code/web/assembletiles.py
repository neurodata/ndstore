#!/usr/bin/python

#
# Assemble tiles into a larger image
#

import Image
import urllib2
from cStringIO import StringIO

class DataInfo:
    tilesize=256
    rows=468
    cols=529
    xMax = 5200*23
    yMax = 5200*26
    # rows=int(math.ceil(5200*23/256))
    # cols=int(math.ceil(5200*26/256))

    #srcwidth=5200
    #srcheight=5200
    #outwidth=256
    #outheight=256
    #root = None
    root = 'http://openconnectomeproject.org/data/brain' # needs to be more flexible
    #rows = 23
    #cols = 26
    #scale = 0
    #maxscale = 10
    #slice = None
    def __init__(self):
        pass

    #def fullWidthInPixels(self):
    #    return self.cols * self.imagewidth

    #def fullHeightInPixels(self):
    #    return self.cols * self.imagewidth

    def getFileLocation(self, scale, slice, row, col):
        return "{0}/{1}/{2}/{3}_{4}.png".format(self.root, scale, slice, col, row) # ARG! need to switch format to row_col

def main(slice=2917,scale=0,cols=1,rows=1,slices=1,row=1,col=1): 

    data = DataInfo()
    
    for tslice in xrange(slice, slice+slices):
        img = Image.new("L", (256*rows, 256*cols) )
        try:
            for trow in xrange(rows):
                for tcol in xrange(cols):
                    filename = data.getFileLocation(scale, tslice, row+trow, col+tcol)
                    tURL = urllib2.urlopen(filename)    # grab image from remote host
                    t = Image.open(StringIO(tURL.read())) 
                    img.paste(t, (256*trow,256*tcol) )
        except:
            # Ignore I/O errors for now, generate blank images
            print 'failed :c'
            pass

        return img
   
if __name__ == "__main__":
    main()
