
import sys

# Test of the annotation service.

# Let's write the voxel file written by annoread to annowrite

# Add the annoate stuff to the paths

import numpy as np
import urllib
import urllib2

import empaths
import dbconfig
import dbconfighayworth5nm
import anndb

voxels = np.load ( "/tmp/voxels.np" )

# Call the web service
try:
  f = urllib2.urlopen ( "http://0.0.0.0:8080/hayworth5nm/npz/3/0,256/0,256/0,4/")
except urllib2.URLError:
  assert 0

url = 'http://0.0.0.0:8080/hayworth5nm/'
values = {'name' : 'Michael Foord',
          'location' : 'Northampton',
          'language' : 'Python' }

data = urllib.urlencode(values)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
the_page = response.read()

print the_page


