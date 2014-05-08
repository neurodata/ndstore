# File for small utlity functions which come handy in OCP
# Feel free to add more as you need them

import time
import os
import pdb

# Function to calcaluate time for a given function. Stores the function in /tmp/
def getTime( filename, func, *args):
  """ Returns the time to implement the function """

  os.chdir('/tmp/')
  f = open(filename, 'a+')
  starttime = time.time()
  returnvalue = func( *args ) 
  endtime = time.time()
  f.write( '{}\n'.format(endtime-starttime) )

  return returnvalue
