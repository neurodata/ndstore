# Copyright 2014 NeuroData (http://neurodata.io)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/python

import trakxml

#
# Simple script to concatenate tiles into larger images.
#

#
# WARNING:
# This script is a temporary hack until we build a better interface to
# retrieve volumes of data.  Use at your own risk.
#

#
# TODO:
#   * Generalize for other datasets other than Boch et al.
#   * Allow X/Y coordinates, and arbitrary image sizes
#

#
# NOTES:
# How to convert a X/Y coordinate in CATMAID to tile coordinates:
# col = x / (256*2^scale)
# row = y / (256*2^scale)
#
# How to convert Z-index from CATMAID to slice numbering:
# slice = z_index + 2916
#
# Each tile is 256x256.
#

#
# Example usage:
# -- Copy images of 4x4 tiles (2048x2048 px) from 25 slices, starting with 3805, to /tmp/out
# python assemble-tiles.py --root=/data/brain --slice=3805 --slices=25 --cols=4 --rows=4 --col=220 --row=300 --scale=0 --outdir=/tmp/out
# -- Same thing, but pulling images from the web
# python assemble-tiles.py --root=http://openconnectomeproject.org/data/brain --slice=3805 --slices=25 --cols=4 --rows=4 --col=220 --row=300 --scale=0 --outdir=/tmp/out
#

import argparse
import errno
import math
import os
import re
import sys
import datetime
import urllib
import StringIO

import Image
import ImageOps

class DataInfo:
    tilesize=256

    # Number of rows at scale=0
    # rows=int(math.ceil(5200*23/256))
    rows=468

    # Number of columns at scale=0
    # cols=int(math.ceil(5200*26/256))
    cols=529

    def __init__(self):
        pass

    def getFileLocation(self, scale, slice, row, col):
        return "{0}/{1}/{2}/{3}_{4}.png".format(self.root, scale, slice, row, col)

    def doesSliceExist(self, slice):
        """Check to see if a slice exists by loading the thumbnail."""
        if self.remote:
            url = "{0}/small/{1}.png".format(self.root, slice)
            print url
            code = urllib.urlopen(url).code
            if code == 200:
                return True
            else:
                return False
        else:
            return os.path.isfile("{0}/small/{1}.png".format(self.root, slice))

    def getImage(self, scale, slice, col, row):
        filename = self.getFileLocation(scale, slice, col, row)
        print filename
        image_file= None
        if self.remote:
            remote_image = urllib.urlopen(filename)
            image_data = remote_image.read()
            image_file = StringIO.StringIO()
            image_file.write(image_data)
            image_file.seek(0)
        else:
            image_file= open(filename, "rb")
        img = Image.open(image_file)
        return img

def main():
    parser = argparse.ArgumentParser(description="Tile images into a larger image")
    parser.add_argument('--root', action="store", required=True, help="Root directory of data (do not include '/0')")
    parser.add_argument('--format', action="store", required=False, default="png", help="Output file format")
    parser.add_argument('--quality', action="store", required=False, default=75, type=int,  help="JPEG Quality")
    parser.add_argument('--slice', action="store", required=True, type=int,  help="First slice to convert (int)")
    parser.add_argument('--slices', action="store", type=int, default=1, help="Number of slices to convert")
    parser.add_argument('--increment', action="store", type=int, default=1, help="Increment between slices")
    parser.add_argument('--useclosest', action="store_true", required=False, default=False, help="Use closest slice if slice does not exist")
    parser.add_argument('--scale', action="store", required=True, type=int, default=0, help="Scale level")
    parser.add_argument('--full', action="store_true", required=False, default=False, help="Read entire slice (do not specify row/col/rows/cols")
    parser.add_argument('--cols', action="store", type=int, default=1, help="Number of columns to copy")
    parser.add_argument('--rows', action="store", type=int, default=1, help="Number of rows to copy")
    parser.add_argument('--row', action="store", type=int, default=0, help="Row to start with")
    parser.add_argument('--col', action="store", type=int, default=0, help="Column to start with")
    parser.add_argument('--outdir', action="store", default=".", help="Output directoy")
    parser.add_argument('--readme', action="store", type=bool, default=True, help="Output README.txt (default)")
    parser.add_argument('--crop', action="store", nargs=4, type=int, required=False, help="Cropping box for final image")
    parser.add_argument('--bbox', action="store", nargs=4, type=int, required=False, help="Bounding box, will set crop/row/rows/col/cols")
    parser.add_argument('--trakem2', action="store", type=bool, default=True, help="Create a trakem2 project")

    args = parser.parse_args()

    data = DataInfo()
    data.root= args.root



    # While the stack info has a path, we would like to avoid using it.
    if data.root.startswith('http://tiles.openconnectomeproject.org/view/kasthuri11/'):
        data.root = "/mnt/data/kasthuri11/"
    if data.root.startswith('http://tiles.openconnectomeproject.org/view/bock11/'):
        args.slice += 2917
        data.root = "/mnt/data/bock11/"

    if data.root.startswith('http://'):
        data.remote = True
    else:
        data.remote = False

    if args.full:
        args.row = 0
        args.col = 0
        # TODO: Figure out why these estimate too many rows/cols
        args.rows = int(math.ceil(data.rows / (2.**args.scale)))
        args.cols = int(math.ceil(data.cols / (2.**args.scale)))
        #args.rows = data.rows / (2**args.scale)
        #args.cols = data.cols / (2**args.scale)

    outHeight = 256*args.rows
    outWidth = 256*args.cols

    if args.bbox:

        # Determine range of boxes needed
        print args.bbox
        firstcol = int(math.floor(args.bbox[0] / (2.**args.scale))) / 256
        firstrow = int(math.floor(args.bbox[1] / (2.**args.scale))) / 256
        lastcol = int(math.ceil(args.bbox[2] / (2.**args.scale))) / 256
        lastrow = int(math.ceil(args.bbox[3] / (2.**args.scale))) / 256
        #args.cols = int(math.ceil((args.bbox[2] - args.bbox[0]) / (2.**args.scale) / 256))
        #args.rows = int(math.ceil((args.bbox[3] - args.bbox[1]) / (2.**args.scale) / 256))

        args.col = firstcol
        args.row = firstrow
        args.cols = (lastcol - firstcol) + 1
        args.rows = (lastrow - firstrow) + 1

        # Calculate cropping region
        args.crop = [
            int((args.bbox[0] / (2.**args.scale)) - firstcol * 256),
            int((args.bbox[1] / (2.**args.scale)) - firstrow * 256),
            int((args.bbox[2] / (2.**args.scale)) - firstcol * 256),
            int((args.bbox[3] / (2.**args.scale)) - firstrow * 256),
            ]

        outWidth = args.crop[2] - args.crop[0]
        outHeight = args.crop[3] - args.crop[1]


    print args.row
    print args.col
    print args.rows
    print args.cols


    try:
        os.makedirs(args.outdir)
    except os.error, e:
        pass

    if (args.slices < 0):
        # Negative range requested
        args.slices = 0 - args.slices
        args.slice = args.slice - args.slices


    if args.readme:
        # Create a README file to describe the images
        readmefile = "{0}/README.txt".format(args.outdir)
        readme = open(readmefile, 'w')
        readme.write("# Generated by {0} at {1}\n".format(os.getenv('LOGNAME'),
          datetime.datetime.now().__str__()))
        readme.write("# Scale: {0}\n".format(args.scale))
        readme.write("# Corner: x={0} y={1}\n".format(args.col*256, args.row*256))
        readme.write("# Size: dx={0} dy={1}\n".format(args.cols*256, args.rows*256))
        readme.write("# Slices: {0}-{1}\n".format(args.slice, args.slice+args.slices-1))
        readme.write("# Increment: {0}\n".format(args.increment))
        readme.close()

    trak = None
    trakfd = None
    if args.trakem2:
        # Create a TrakEM2 project description
        trak = trakxml.TrakXML()
        trakfile = "{0}/trak.xml".format(args.outdir)
        trakfd = open(trakfile, 'w')
        trak.writeHeader(trakfd)
        trak.writeBody(trakfd, outHeight, outWidth)
        

    for slice in xrange(args.slice, args.slice+args.slices, args.increment):
        print "Working on slice {0}...".format(slice)
        if args.useclosest:
            slicefound = False
            for delta in xrange(0,args.increment):
                # Check following slices, up to the increment level
                if data.doesSliceExist(slice+delta):
                    slicefound = True
                    slice = slice + delta
                    break
            if not slicefound:
                # Go to next slice
                continue
        elif not data.doesSliceExist(slice):
            print "Slice {0} does not exist".format(slice)
            # Slice does not exist, and we are not going to find a neighbor
            continue

        img = Image.new("L", (256*args.cols,256*args.rows) )
        try:
            for col in xrange(args.cols):
                for row in xrange(args.rows):
                    t = data.getImage(args.scale, slice, args.row+row, args.col+col)
                    img.paste(t, (256*col,256*row) )
        except:
            # Ignore I/O errors  -- the image will remain black
            # This is most likely a sign of a non-existent slice
            # TODO: Find a better way of handling this.
            #pass
            raise
        if args.crop:
            img = img.crop(tuple(args.crop))

        outfilename = None
        outfilepath = None
        fileformat = args.format.lower()
        if (fileformat == "png"):
            outfilename = "{1}.png".format(args.outdir, slice)
            outfilepath = "{0}/{1}".format(args.outdir, outfilename)
            img.save(outfilepath, format="PNG", optimize=1)
        elif (fileformat == "jpg" or fileformat == "jpeg"):
            outfilename = "{1}.jpg".format(args.outdir, slice)
            outfilepath = "{0}/{1}".format(args.outdir, outfilename)
            img.save(outfilepath, format="JPEG", quality=args.quality)
        else:
            print "Invalid format: {0}".format(fileformat)

        print outfilepath

        if args.trakem2:
            trak.writeLayer(trakfd, slice, outfilename, outHeight, outWidth)

    if args.trakem2:
        trak.writeFooter(trakfd)
        trakfd.close()
   
if __name__ == "__main__":
    main()
