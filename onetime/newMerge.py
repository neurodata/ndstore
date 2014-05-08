import urllib2
import argparse
import numpy as np
import urllib2
import cStringIO
import sys

import tempfile
import h5py

def main():

  parser = argparse.ArgumentParser(description='Merge double labeled voxels')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('--resolution', type=int, action="store", help='Resolution at which you want the voxels.  Defaults to 1.', default=1)

  result = parser.parse_args()

  #Divide the database into regions and  get the exceptions for each region
  # To belgine with I am hacking this 

  cury = 2048 * 26
  count = 0

#Hardcoded for LP4's range ( to change)
  #for y in range(5120,59903,5120/2):
  #failed URL http://localhost/ocp/ocpca/bock11_octSynLP4/exceptions/1/20000,23000/7680,10240/3238,3253/
  for y in range(cury+2048,cury+4096,2048):
    curz = 2917
    for z in range(2933,4156,16):         
  
#      url = "http://%s/ocp/ocpca/%s/exceptions/%s/20000,23000/%s,%s/%s,%s/" % (result.baseurl,result.token, result.resolution, cury,y,curz,z)
      url = "http://%s/ocpca/%s/exceptions/%s/20000,23000/%s,%s/%s,%s/" % (result.baseurl,result.token, result.resolution, cury,y,curz,z)
      print "Fetching " + url
      curz = z+1
      count = count+1
      listOfSets= []
  # Get exceptions for the region
      try:
        f = urllib2.urlopen ( url )
      except urllib2.URLError, e:
        print "Failed URL", url
        print "Error %s" % (e) 
        sys.exit(0)

      print "Processing " + url

  # Read into a temporary file
      tmpfile = tempfile.NamedTemporaryFile ( )
      tmpfile.write ( f.read() )
      tmpfile.seek(0)
      h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

# The exceptions are of the form x,y,x, id1, id2....
      if  h5f.get('exceptions'):
        listOfSets = list(h5f['exceptions'][:])
    # At this point we have a list of numpy arrays
        
# one time conversion for the first element
        if len(listOfSets) <= 3:
          continue;
      first_set = listOfSets[0]
      listOfSets[0] = set(first_set[3:])
      listOfSets[0].discard(0)

      first = True

# Combine the exceptions to get one disjoint set of exceptions.Each element in the set represents ids that have tp be merged
      while True:
        merged_one = False
        supersets = [listOfSets[0]]
      
        for elm in listOfSets[1:]:
          if first:
            s = set(elm[3:])
            s.discard(0)
          else:
            s = set(elm)
            s.discard(0)
          in_super_set= False
          for ss in supersets:
            if s & ss:
              ss |= s
              merged_one = True
              in_super_set = True
              break
          
          if not in_super_set:
            supersets.append(s)
        #     print supersets
        if not merged_one:
          break
        

        listOfSets = supersets
        first = False

      h5f.close()

      # Each element in the superset corresponds to onelist of ids that has to be merged
      print "==================Merging annotations========================"
      print "Number of merge calls %s" % len(supersets)
      for elm in supersets:
        # RB don't merge singles
        if len(elm) == 1:
          continue
        mergeids = ','.join([str(n) for n in elm]) 
        #url="http://%s/ocp/ocpca/%s/merge/%s/global/%s/"%(result.baseurl,result.token, mergeids, result.resolution)
        url="http://%s/ocpca/%s/merge/%s/global/%s/"%(result.baseurl,result.token, mergeids, result.resolution)
        print url
        try:
          f = urllib2.urlopen ( url )
        except urllib2.URLError, e:
          print "Failed URL", url
          print "Error %s" % (e)
          sys.exit(0)
    # Increment the Y region    
    cury=y

  print count

if __name__ == "__main__":
  main()

