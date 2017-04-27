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

import urllib
import boto3
import blosc
import time
import numpy as np
from PIL import Image

def handler_name(event, context):
  
  print('Starting Function')
  start_time = time.time()
  # get bucket name from the event
  tile_bucket_name = event['Records'][0]['s3']['bucket']['name']
  cuboid_bucket_name = 'neurodata-cuboid-store-test'
  s3 = boto3.resource('s3')
  tile_bucket = s3.Bucket(tile_bucket_name)
  cuboid_bucket = s3.Bucket(cuboid_bucket_name)
  # the image name is key
  image_name = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')
  alpha_value, slice_number = image_name.strip('.png').split('_')
  slice_number = int(slice_number)
  cube_size = [512, 512, 64]
  if slice_number%64 == (cube_size[2]-1):
    slab = np.zeros([64,512,512], dtype=np.uint8)
    print("Cube shape:{}".format(slab.shape))
    for i in range(cube_size[2]):
      try:
        key = '{}_{}.png'.format(alpha_value, i)
        #print('KEY {}'.format(key))
        data = s3.Object(tile_bucket_name, key).get()['Body'].read()
        slab[i,:,:] = np.asarray(Image.frombuffer('L', (512,512), data, 'raw', 'L', 0, 1))
      except Exception as e:
        print(e)
        raise(e)
    try:
      response = cuboid_bucket.put_object(
          Body = blosc.pack_array(slab),
          Key = '{}_{}'.format(alpha_value, slice_number)
      )
      print("Inserting {}".format('{}_{}'.format(alpha_value, slice_number)))
    except Exception as e:
      print(e)
      raise e
  print('Ending function. Time:{}'.format(time.time()-start_time))
  return None
