#!/usr/bin/python3

import os
import math
import argparse

from PIL import Image, ImageSequence, ImageColor, ImageOps
import numpy as np

#
# First pass to read mouse light data & export into CATMAID tiles.
# WARNING: Python tuples are (x,y,z) but numpy arrays are (z,y,x)
#

class MouseStack:
  def __init__(self, path, globalsize, tilesize, channels):
    self.path = path.rstrip('/')
    self.globalsize = globalsize
    self.tilesize = tilesize
    self.channels = channels

    # Maximum directory depth (number of levels in the scale pyramid)
    self.max_depth = int(math.ceil(math.log2(max(
                            self.globalsize[0]/self.tilesize[0],
                            self.globalsize[1]/self.tilesize[1],
                            self.globalsize[2]/self.tilesize[2]
                        ))))

  def toBitString(self, i, depth=None):
    """Generate a bitstring for 'i' for up to self.max_depth bytes."""

    if depth == None:
        depth = self.max_depth

    s = []
    for b in reversed(range(depth)):
        s.append((i & 1<<b)>>b)

    return s

  def getTilePath(self, x, y, z, channel, scale=0):
    """Get the tile path associated with a given X,Y,Z."""

    # Total number of directories to traverse

    # Reduce by scale requested
    steps = self.max_depth - scale

    tile_x = x // (self.tilesize[0] * 2**scale)
    tile_y = y // (self.tilesize[1] * 2**scale)
    tile_z = z // (self.tilesize[2] * 2**scale)

    levels = []
    for (xb,yb,zb) in zip(self.toBitString(tile_x, steps),
                        self.toBitString(tile_y, steps),
                        self.toBitString(tile_z, steps)):
        total = zb*4+yb*2+xb
        levels.append(total+1)

    path = self.path + '/' +  '/'.join(str(x) for x in levels) + "/default.%d.tif" % channel
    return path



#
# Data description:
#   Colums: 40768/637=64
#   Rows: 25792/403=64
#   Layers: 14272/233=61.25321 (62)
#   Channels: 2 [0, 1]

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--data', default='/nobackup/mousebrainmicro/2014-11-24-Stitch1/', help='Data directory')
  parser.add_argument('--globalsize', nargs=3, type=int, metavar=('X', 'Y', 'Z'), help='Total size of mosaic', default=[43520, 38656, 16384])
  parser.add_argument('--tilesize', nargs=3, type=int, metavar=('X', 'Y', 'Z'), help='Size of tif tiles', default=[680, 604, 256])
  parser.add_argument('--channels', nargs='+', type=int, help="Channels to processs", default=[0, 1])
  parser.add_argument('--slices', nargs='+', type=int, default=None, help="Specific Z-slab to process [Default: (all)]")
  parser.add_argument('--scales', nargs='+', type=int, default=[0], help="Scales to generate [Default: (all)]")
  parser.add_argument('--output', default="/tier2/bock/nobackup/tiles/cluster/mouse/test1/", help="Path to output tiles to.")

  args = parser.parse_args()
  
  stack = MouseStack(args.data, args.globalsize, args.tilesize, args.channels)


  # TODO: Encode per-channel levels into the parser arguments?
  # Mike: "0 is green, 1 is red (or even better - magenta)"
  # levels[channel] = (black,white)
  levels = {0 : (13200, 32000),
            1 : (11200, 30000)}

  # Color for each channel
  color = {0 : (0,255,0),
           1 : (255,0,255)}

  # Threshold for data (don't emit if no data above this)
  data_output_threshold = 2**5

  if args.slices is not None:
      slices = sorted(args.slices)
  else:
      # Generate full list of slices
      slices = list(range(int(math.ceil(stack.globalsize[2]/stack.tilesize[2]))))

  # Note: Concept of scales is incompatible with CATMAID -- CATMAID uses layers & does not scale in Z yet
  if args.scales is not None:
      scales = sorted(args.scales, reverse=True)


  # Number of smaller tiles into a larger tile
  tiles_per_col = 2
  tiles_per_row = 2

  print(scales)
  for scale in scales:
      for slicen in slices:
          for bigrow in range(stack.globalsize[1] // (stack.tilesize[1]*tiles_per_row*2**scale)):
              for bigcol in range(stack.globalsize[0] // (stack.tilesize[0]*tiles_per_col*2**scale)):
                  for channel in args.channels:
                      slabdata = np.zeros([256, 604*tiles_per_row, 680*tiles_per_row], dtype=np.uint16)
                      for smallrow in range(tiles_per_row):
                          for smallcol in range(tiles_per_col):
                                  #filename = '/nobackup/mousebrainmicro/2014-11-24-Stitch1/5/8/3/1/8/5/default.%d.tif' % channel
                                  col = (bigcol*tiles_per_col + smallcol) * stack.tilesize[0]
                                  row = (bigrow*tiles_per_row + smallrow) * stack.tilesize[1]
                                  z = slicen * stack.tilesize[2]

                                  filename = stack.getTilePath(col,row,z,channel,scale)
                                  if os.path.exists(filename):
                                      print("Reading %s ..." % filename)
                                      im = Image.open(filename)
                                       
                                      
                                      # Read image data
                                      # TODO: Consider using skimage.io.* instead?
                                      #tiledata = np.empty([223,403,637], dtype=np.uint16)
                                     
                                      frameNumber = 0
                                      for frame in ImageSequence.Iterator(im):
                                          imarray = np.array(frame)
                                          slabdata[frameNumber,
                                              smallrow*stack.tilesize[1]:(smallrow+1)*stack.tilesize[1],
                                              smallcol*stack.tilesize[0]:(smallcol+1)*stack.tilesize[0]] = imarray

                                          #print(frameNumber,
                                          #    smallrow*stack.tilesize[1],(smallrow+1)*stack.tilesize[1],
                                          #    smallcol*stack.tilesize[0],(smallcol+1)*stack.tilesize[0])
                                          #print(smallcol, smallrow)
                                          #print (imarray.shape)
                                          #print (slabdata.shape)
                                          #print("Non zero: %d" % np.count_nonzero(slabdata))
                                          frameNumber += 1
                                  else:
                                      print("File does not exists: %s" % filename)



                      # Export tiles to disk
                      # Is there any data?  Skip if not..
                      if not slabdata.any():
                          print("No data in slab!  Skipping output.")
                          continue

                      # Convert the entire array down to 8bit w/ fixed contrast values
                      # TODO: Figure out how to do this with fewer operations?
                      if channel in levels:
                          (black, white) = levels[channel]
                          ratio = 255 / (white - black)
                          slabdata[slabdata < black] = black
                          slabdata[slabdata > white] = white 
                          slab8bit = ((slabdata - black) * ratio).astype(np.uint8)
                      else:
                          print("No level information found.  Doing naive conversion.")
                          slab8bit = (slabdata/8).astype(np.uint8)


                      for frame in range(stack.tilesize[2]):
                          if np.nanmax(slab8bit[frame]) < data_output_threshold:
                              print("No data in frame %d!  Skipping." % frame)
                              continue

                          z = slicen*stack.tilesize[2] + frame
                          col = bigcol
                          row = bigrow

                          im = Image.fromarray(slab8bit[frame])

                          # Inefficient way to colorize...
                          im = ImageOps.colorize(im, black=(0,0,0), white=color[channel]).convert('P', palette=Image.ADAPTIVE, colors=256)
                          #print("Node ", im.mode)

                          outpath = "%s/c%d/%d/%d/%d" % (args.output, channel, scale, z, row)
                          if not os.path.exists(outpath):
                              os.makedirs(outpath)

                          outfile = "%s/%s.png" % (outpath,col)

                          #im.save("/tmp/out/%d.%d.%d.%d.png" % (z, col, row, channel))
                          print(outfile)
                          im.save(outfile, optimize=1)



if __name__ == "__main__":
    main()
