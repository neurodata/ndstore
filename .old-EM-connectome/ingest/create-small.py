#!/usr/bin/python

#
# Create the 'small' (192x192) preview window for catmaid.
# We use the scale '9' images as a source.  The only trickery
# is to rescale the image based on the dimensions of the
# original image -- not that of the two tiles.
#

import argparse
import errno
import math
import os
import re
import sys

import Image
import ImageOps

class DataInfo:
    srcwidth=5200
    srcheight=5200
    outwidth=256
    outheight=256
    root = None
    rows = 23
    cols = 26

    def __init__(self):
        pass

    def fullWidthInPixels(self):
        return self.cols * self.imagewidth

    def fullHeightInPixels(self):
        return self.cols * self.imagewidth

    def getFileLocation(self, scale, col, row):
        return "{0}/{1}/{2}/{3}_{4}.png".format(self.root, scale, self.slice, row, col)

    def getSmallFileLocation(self):
        return "{0}/small/{1}.png".format(self.root, self.slice)

def main():
    parser = argparse.ArgumentParser(description="Create a small thumbnail image")
    parser.add_argument('root', action="store", help="Root directory of data (do not include '/0')")
    parser.add_argument('slice', action="store", type=int,  help="Slice to convert (int)")

    args = parser.parse_args()

    data = DataInfo()
    data.root= args.root
    data.slice = args.slice

    # We are reading in level 9 (two tiles)
    img = Image.new("L", (256*2,256) )
    for x in xrange(2):
        t = Image.open(data.getFileLocation(9,x,0))
        img.paste(t, (256*x,0) )
   
    # 5200*26 / (2^9) = 264
    # 5200*23 / (2^9) = 233
    img = img.crop( (0, 0, 264, 233) )
    img.thumbnail( (192,192), Image.ANTIALIAS )
    img.save(data.getSmallFileLocation(), format="PNG", optimize=1)


if __name__ == "__main__":
    main()
