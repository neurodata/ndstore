import urllib2
import zlib
import StringIO
import numpy as np
import argparse
import cStringIO
import sys
import time

def main():

  parser = argparse.ArgumentParser(description='Cutout a portion of the database.')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('dataset', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('resolution', action="store", type=int )
  parser.add_argument('xlow', action="store", type=int )
  parser.add_argument('xhigh', action="store", type=int)
  parser.add_argument('ylow', action="store", type=int)
  parser.add_argument('yhigh', action="store", type=int)
  parser.add_argument('zlow', action="store", type=int)
  parser.add_argument('zhigh', action="store", type=int)

  result = parser.parse_args()

  #url = 'http://' + result.baseurl + '/emca/' + result.dataset + '/npz/' +\
  #          str(result.resolution) + "/" +\
  #          str(result.xlow) + "," + str(result.xhigh) + "/" +\
  #          str(result.ylow) + "," + str(result.yhigh) + "/" +\
  #          str(result.zlow) + "," + str(result.zhigh) + "/"\

#  url = "http://localhost/emca/ac3/npz/1/5472,6496/8712,9224/1000,1016/"


#URL for 16*16*4( 2^10)
#  url = "http://localhost/emca/ac3/npz/1/5472,5488/8712,8728/1000,1004/"
#URL for 16*16*8( 2^11)                                                                                      

 # url = "http://localhost/emca/ac3/npz/1/5472,5488/8712,8728/1000,1008/"
#URL for 16*16*16( 2^12)                                                                                        
  #url = "http://localhost/emca/ac3/npz/1/5472,5488/8712,8728/1000,1016/"
#URL for 32*16*16( 2^13)                                                                                        
  #url = "http://localhost/emca/ac3/npz/1/5472,5504/8712,8728/1000,1016/"
#URL for 32*32*16( 2^14)                                                                                        
 # url = "http://localhost/emca/ac3/npz/1/5472,5504/8712,8744/1000,1016/"
#URL for 64*32*16( 2^15)                                                                                        
  #url = "http://localhost/emca/ac3/npz/1/5472,5536/8712,8744/1000,1016/"
#URL for 64*64*16( 2^16)                                                                                        
  #url = "http://localhost/emca/ac3/npz/1/5472,5536/8712,8776/1000,1016/"
#URL for 128*64*16( 2^17)                                                                                       
 # url = "http://localhost/emca/ac3/npz/1/5472,5600/8712,8776/1000,1016/"
 #URL for 128*128*16(2^18)
  #url = "http://localhost/emca/ac3/npz/1/5472,5600/8712,8840/1000,1016/"
#URL for 128*128*32(2^19)
  url = "http://localhost/emca/ac3/npz/1/5472,5600/8712,8840/1000,1032/"

#URL for 128*128*64(2^20)
  #url = "http://localhost/emca/ac3/npz/1/5472,5600/8712,8840/1000,1064/"
#URL for 128*128*128(2^21)
 # url = "http://localhost/emca/ac3/npz/1/5472,5600/8712,8840/1000,1128/"
#URL for 512*512*16(2^22)
  #url = "http://localhost/emca/ac3/npz/1/5472,5984/8712,9224/1000,1016/"
#URL for 1024*512*16(2^23)
#  url = "http://localhost/emca/ac3/npz/1/5472,6496/8712,9224/1000,1016/"
#URL for 1024*1024*16(2^24)
  #url = "http://localhost/emca/ac3/npz/1/5472,6496/8712,9436/1000,1016/"
#URL for 1024*1024*32(2^25)
  #url = "http://localhost/emca/ac3/npz/1/5472,6496/8712,9436/1000,1032/"
#URL for 1024*1024*32(2^26)
#  url = "http://localhost/emca/ac3/npz/1/5472,6496/8712,9436/1000,1064/"
#URL for 1024*1024*64(2^27)
#url = "http://localhost/emca/ac3/npz/1/5472,6496/8712,9436/1000,1128/"
#URL for 1024*1024*128(2^28)
#url = "http://localhost/emca/ac3/npz/1/5472,6496/8712,9436/1000,1256/"




  #  Grab the bottom corner of the cutout
  xoffset = result.xlow
  yoffset = result.ylow
  zoffset = result.zlow

  print "Getting ",  url

  try:
    f = urllib2.urlopen ( url )
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s" % (e.read()) 
    sys.exit(0)

  zdata = f.read ()

  print "Retrieved"

  # get the data out of the compressed blob
  pagestr = zlib.decompress ( zdata[:] )
  pagefobj = StringIO.StringIO ( pagestr )
  cube = np.load ( pagefobj )

#  annodata = np.zeros( [ result.zhigh - result.zlow, result.yhigh - result.ylow, result.xhigh-result.xlow ] )

 # vec_func = np.vectorize ( lambda x: 0 if x > 30 else 125 ) 
 # annodata = vec_func ( cube )

 # print np.nonzero ( annodata )
#-------------------
  start = time.time()
  url = 'http://%s/emca/%s/npdense/%s/%s,%s/%s,%s/%s,%s/' % ( result.baseurl, result.token, result.resolution, result.xlow+1024, result.xhigh+1024, result.ylow, result.yhigh, result.zlow, result.zhigh ) 


  # Encode the voxelist an pickle
  fileobj = cStringIO.StringIO ()
  np.save ( fileobj, cube )
  cdz = zlib.compress (fileobj.getvalue())

  print "Posting to", url

  # Build the post request
  req = urllib2.Request(url, cdz)
  response = urllib2.urlopen(req)
  the_page = response.read()
  end = time.time()

#-------------------------
  print "Done"
  print end-start
if __name__ == "__main__":
      main()



