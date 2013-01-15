import os
import shutil

inputdir = '/data/EM/bumbarger13'
outputdir = '/data/EM/bumbarger13.small'

# resolutions
highres = 4   # 0 to 4

# Active slices at resolution 
# x = 11-14
# y = 10-13
xrange = (11,15)
yrange = (10,14)

# geometry of the space at high resolution
xtiles = xrange[1]-xrange[0]
ytiles = yrange[1]-yrange[0]

# need to loop on this later
slices = [0]

# build the directories
for res in range(highres+1):

  #outer directory is resolution
  dirname = "%s/%s" % ( outputdir, res )
  if not os.path.exists ( dirname ):
    os.mkdir ( dirname )

  #inner directory is slicenumber
  for slice in slices:
    dirname = "%s/%s/%s" % ( outputdir, res, slice )
    if not os.path.exists ( dirname ):
      os.mkdir ( dirname )


for res in range(highres,-1,-1):
  for ytile in range(xtiles*2**(highres-res)):
    for xtile in range(ytiles*2**(highres-res)):

      xoffset = xrange[0]*2**(highres-res) 
      yoffset = yrange[0]*2**(highres-res)

      infile = "%s/%s/%s_%s_%s.png" % ( inputdir, slice, ytile+yoffset, xtile+xoffset, res )
      outfile = "%s/%s/%s/%s_%s.png" % ( outputdir, res, slice, ytile, xtile )

      try:
        if not os.path.exists(outfile):
          print "Copying %s to %s" % ( infile, outfile )
          shutil.copy ( infile, outfile )
        else: 
          print "Found %s" % ( outfile )
      except:
        print "Missing file %s" % ( infile )

