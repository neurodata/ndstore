#!/usr/bin/python

#
# Script to re-tile the image files from Bock et al.
# The source images are 5200x5200 tiles in a 26x23 grid.
# The output tiles are 256x256 for use with CATMAID.
#

#
# The following scheme is being used for the images:
#
# <scale>/<slice>/<row>_<col>.png
#
# The terms are defined the same as they are in Catmaid, but
# this file organizations seems far more reasonable and allows
# us to ship lower-resolution versions of the data with ease.
#

#
# CATMAID tile format:
# """
# Tiles are ordered by file name convention.  Each section is stored in
# a directory whose name is the section index.  A tile's name contains
# the row and column in tile coordinates and the scale index i where
# f = 1/2i is the scale factor relative to the original resolution.
# For example, "4/14 20 2.jpg" identifies the tile at row 14 and column
# 20 in section 4 at scale level 2.
# """
# CATMAID: Collaborative Annotation Toolkit for Massive Amounts of Image Data
# Saalfeld et al., April 2009
#

#
# Note:
#    * This code is a hack, and should probably be cleaned up before anyone
#      else uses it.
#    * This script is a memory hog, caching entire columns of the source image
#      to improve performance.  A 64-bit compiled Python may be required.
#

import argparse
import errno
import os
import re
import sys

import Image

def getOutputFileName(slice, x, y):
    """Return the root filename for a tile cornered at X,Y in layer Z"""
    row = x % 256
    col = y % 256

    return "{0}/{1}_{2}_{3}".format(slice, row, col, 1)


class DataInfo:
    srcwidth=5200
    srcheight=5200
    outwidth=256
    outheight=256
    srcdir=None
    outdir=None
    rows = 23
    cols = 26
    scale = 0
    slice = None

    def __init__(self):
        pass

    def fullWidthInPixels(self):
        return self.cols * self.imagewidth

    def fullHeightInPixels(self):
        return self.cols * self.imagewidth

    def getFileName(self, col, row):
        # +1 is added here to allow for C-style numbering elsewhere
        return "{0}/c{1:02}r{2:02}.tif".format(self.srcdir, col+1, row+1)

    def getOutputFileLocation(self, col, row):
        return "{0}/{1}/{2}/{3}_{4}.png".format(self.outdir, self.scale, self.slice, row, col)

    def makeDirs(self):
        dir = "{0}/{1}/{2}/".format(self.outdir, self.scale, self.slice)
        try:
            os.makedirs(dir)
        except os.error, e:
            pass

    def getFullColumn(self, colid):
        return FullColumn(self, colid)

class FullColumn:
    """Read and store a complete column of image data."""
    data = None
    colid = None
    img = None

    def __init__(self, data, colid):
        self.data = data
        self.colid = colid

        if (colid >= data.cols):
            # Return a blank (black) image if we are past the edge.
            # Needed when the source image size is not evenly divisible by output tile size
            self.img = Image.new("L", (data.srcwidth,data.srcheight*data.rows) )
            return

        self.img = Image.new("L", (data.srcwidth,data.srcheight*data.rows), None )

        for rowid in xrange(0, data.rows):
            filename = data.getFileName(colid, rowid)
            print("Reading " + filename)
            fimg = Image.open(filename)
            self.img.paste(fimg, (0, data.srcheight*rowid, data.srcwidth, data.srcheight*(rowid+1)) )

        # Test to see if we read hte strip corretly

    def basePixel(self):
        return data.srcwidth * self.colid

 
def main():
    parser = argparse.ArgumentParser(description="Create small tiles from the source tiff files")
    parser.add_argument('srcdir', action="store", help="Where to read data from")
    parser.add_argument('outdir', action="store", help="Root directory for output tiles")
    parser.add_argument('--slice', action="store", type=int, default=-1,
      help="Override slice detection from directory name")
    args = parser.parse_args()

    data = DataInfo()
    data.srcdir = args.srcdir
    data.outdir = args.outdir

    slice = None

    if args.slice >= 0:
        data.slice = args.slice
    else:
        # Determine slice from the directory name ( i.e., ../z2919/ )
        s = re.search("^.*/z(\d+)/?$", args.srcdir)
        if s:
            data.slice = int(s.group(1))
        else:
            raise Exception("Slice could not be determined. Use --slice to override")
        
    data.makeDirs()

    # Now do the work...
    fullrow = None
    fullrow2 = None
    for colpx in xrange(0, data.cols * data.srcwidth, 256):
        startcol = colpx / data.srcwidth
        endcol = (colpx + 255) / data.srcwidth
        border = False
        if not fullrow or fullrow.colid != startcol:
            # We've crossed into a new column (possibly the first) 
            fullrow = data.getFullColumn(startcol)

        if startcol != endcol:
            # Tiles in this column will cross into the neighboring source column
            border = True
            fullrow2 = data.getFullColumn(endcol)

        for rowpx in xrange(0, data.rows * data.srcheight, 256):
            image = None
            if border:
                # Complex case: Tile crosses two source columns
                image = Image.new("L", (256,256), None)

                # Rows will be the same from both sources
                y1 = rowpx
                y2 = rowpx + 256

                # Copy from the first column
                x1 = colpx % data.srcwidth
                x2 = endcol * data.srcwidth
                region = fullrow.img.crop( (x1,y1,x2,y2) )
                image.paste(region, (0,0))

                # Next, copy the second column
                x1 = 0
                x2 = (colpx + 256) % data.srcwidth
                region = fullrow2.img.crop( (x1,y1,x2,y2) )
                image.paste(region, (256-x2,0))

            else:
                # Simple case: direct copy
                x1 = colpx % data.srcwidth
                x2 = colpx % data.srcwidth + 256
                y1 = rowpx
                y2 = rowpx + 256
                image = fullrow.img.crop( (x1, y1, x2, y2) )

            # Write image to disk
            filename = data.getOutputFileLocation(colpx / 256, rowpx / 256)
            image.save(filename, format="PNG", optimize=1)

        if border:
            # Tidy up.  The second column is now the primary column.
            fullrow = fullrow2
            fullrow2 = None
    
if __name__ == "__main__":
    main()
