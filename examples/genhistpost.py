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

def main():

    parser = argparse.ArgumentParser(description='Start a histogram by getting/posting some JSON parameters to the histogram service.')
    parser.add_argument('baseurl', action='store', help='e.g. brainviz1.cs.jhu.edu/microns/nd')
    parser.add_argument('token', action='store')
    parser.add_argument('channel', action='store')
    parser.add_argument('--roi', nargs='*', action='store', help='A series of coordinate pairs in the following format: x0,y0,z0-x1,y1,z1')
    parser.add_argument('--ramon', action='store', help='A comma separated list of RAMON IDs to use for ROI locations: idx0,idx1,idx2,...')

    result = parser.parse_args()

    if result.roi:
        # parse ROI list
        data = {'ROI': []}
        for roicords in result.roi:
            roicords_str = roicords.split('-')
            roicords_tpl = ("({})".format(roicords_str[0]), "({})".format(roicords_str[1]))
            data['ROI'].append( roicords_tpl )

    elif result.ramon:
        # parse RAMON list
        data = {'RAMON': ''}
        data['RAMON'] = result.ramon.split(',')

    else:
        # post empty data which should start standard histogram generation
        data = {}

    # post
    url = "http://{}/stats/{}/{}/genhist/".format( result.baseurl, result.token, result.channel )

    print "Preparing to post {} data containing {} to {}".format( data.keys()[0], data.values()[0], url)
    raw_input("Press any key to continue...")

    r = requests.post(url, json=data)
    if r.status_code == 200:
        print "Post request succeeded."
    else:
        print "Error: Post request failed (status code: {})".format(r.status_code)



if __name__ == '__main__':
    main()
