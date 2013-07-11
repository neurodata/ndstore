import numpy as np

#
#  filterCutout
#
def filterCutout ( cutout, filterlist ):
  """Remove all annotations in a cutout that do not match the filterlist"""

  # dumbest implementation
  for z in range(cutout.shape[0]):
    for y in range(cutout.shape[1]):
      for x in range(cutout.shape[2]):
        if cutout[z,y,x] not in filterlist:
          cutout[z,y,x] = 0
          

