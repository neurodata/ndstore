# Copyright 2016 NeuroData (http://neurodata.io)
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

import sys, os
import requests
import argparse
import re

import tempfile
import h5py
import urllib2
import json

import numpy as np

def getBoundingBox(baseurl, token, channel, ramonobj, res):
    """ Gets the bounding box for a given RAMON object. Returns (low, high) """
    url = "http://{}/sd/{}/{}/{}/boundingbox/{}/".format( baseurl, token, channel, ramonobj, res )

    try:
        f = urllib2.urlopen( url )
    except urllib2.URLError, e:
        print "Failed to open URL: {}".format(e)
        sys.exit(0)

    # create in memory h5 file to read result
    tmpfile = tempfile.NamedTemporaryFile()
    tmpfile.write( f.read() )
    tmpfile.seek(0)
    h5f = h5py.File(tmpfile.name, driver='core', backing_store=False)

    keys = h5f.keys()

    # assume one annotation, return after the first iteration
    for k in keys:
        idgrp = h5f.get(k)
        xyzdim = idgrp['XYZDIMENSION']
        xyzoff = idgrp['XYZOFFSET']

        low = np.array(xyzoff)
        high = np.array(xyzdim)

        return low, high

    return None, None

def startHistJob(baseurl, token, channel, roi):
    url = "http://{}/stats/{}/{}/genhist/".format( baseurl, token, channel )

    r = requests.post(url, json={'ROI': [roi]})
    if r.status_code == 200:
        return True
    else:
        print "Error: Post request to generate histogram failed (status code: {})".format(r.status_code)
        print r.text
        return False

def main():

    parser = argparse.ArgumentParser(description='Generate a histogram for an ROI given by the bounding box of a RAMON object')
    parser.add_argument('baseurl', action='store', help='e.g. brainviz1.cs.jhu.edu/microns/nd')
    parser.add_argument('anntoken', action='store')
    parser.add_argument('annchannel', action='store', help='Channel containing the RAMON object')
    parser.add_argument('ramonobj', action='store', help='RAMON object ID')
    parser.add_argument('--imagetoken', action='store', help='Optional image token (if different from annotoken)')
    parser.add_argument('imagechannel', action='store', help='Image data channel (where the histogram will be generated)')
    parser.add_argument('resolution', action='store', type=int, help='Resolution for the RAMON object / bounding box (should be the default resolution for the image data channel).')
    parser.add_argument('--output', action='store', help='Filename for writing the output to disk')

    result = parser.parse_args()
    baseurl = result.baseurl
    anntoken = result.anntoken
    annchannel = result.annchannel
    ramonobj = result.ramonobj
    if result.imagetoken:
        imtoken = result.imagetoken
    else:
        imtoken = anntoken
    imchannel = result.imagechannel
    res = result.resolution

    # first, get the bounding box for the RAMON object
    corner, dim = getBoundingBox(baseurl, anntoken, annchannel, ramonobj, res)

    roi = []
    roi.append(corner.tolist())

    # convert dim to the opposite corner
    topcorner = np.zeros(3, dtype=np.uint32)
    for idx, coord in enumerate(corner):
        topcorner[idx] = coord + dim[idx]
    roi.append(topcorner.tolist())
    print roi

    # then run the histogram job for the bounding box
    if startHistJob(baseurl, imtoken, imchannel, roi):
        # finally, output the bounding box to the user in a json file
        if result.output:
            with open(result.output, 'wb') as f:
                json.dump({ramonobj:roi}, f)

if __name__ == '__main__':
    main()
