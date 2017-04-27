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

import os
import sys
import boto3
import boto
import six
import time
import cStringIO
import numpy as np
import argparse
import multiprocessing as mp
import Queue
from PIL import Image
sys.path.append(os.path.abspath('../'))
from ndingest.settings.settings import Settings
ndingest_settings = Settings.load()

class Uploader(object):

  def __init__(self, num_processes=2):
    # self.bucket_name = 'neurodata-tile-store-test'
    self.num_processes = num_processes
    self.task_queue = mp.JoinableQueue()
    # self.s3 = boto.connect_s3()
    s3 = boto3.resource('s3', aws_access_key_id='AKIAIQ6LNQRHEYXBUSGA', aws_secret_access_key='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')
    self.bucket = s3.Bucket('neurodata-tile-store-test')
    # self.bucket = self.s3.lookup(self.bucket_name)
    self.n_tasks = 0

  def queue_task(self, key, data):

    self.task_queue.put((key, data))
    self.n_tasks += 1

  def worker(self, input):

    print('starting worker')
    while 1:
      try:
        (key, data) = input.get(True, 1)
        # print '{}:{}'.format(key, data)
      except Queue.Empty:
        print('no more tasks')
        break
        sys.exit(0)
      data.seek(0)
      try:
        print("Uploading {}".format(key))
        response = self.bucket.put_object(
            Body = data.read(),
            Key = key
        )
        input.task_done()
      except Exception as e:
        print(e)
        raise e


# def upload((key, data)):
  # s3 = boto3.resource('s3', aws_access_key_id='AKIAIQ6LNQRHEYXBUSGA', aws_secret_access_key='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')
  # bucket = s3.Bucket('neurodata-tile-store-test')
  # try:
    # response = bucket.put_object(
        # Body = data.read(),
        # Key = key,
    # )
    # return response
  # except Exception as e:
    # print(e)
    # raise e

def main():
  parser = argparse.ArgumentParser(description='Test upload')
  parser.add_argument('num', action='store', type=int, help='Number of threads')
  parser.add_argument('--iter', dest='iteration', action='store', type=int, default=1, help='Size of data')
  parser.add_argument('--trigger', dest='trigger', action='store_true', default=False, help='Trigger')
  result = parser.parse_args()
  
  key_list = []
  data_list = []
  
  up = Uploader(result.num)
  import pdb; pdb.set_trace()
  
  if result.trigger is False:
    for j in range(result.iteration):
      for i in range(64):
        data = np.random.randint(256, size=(512,512), dtype=np.uint8)
        image_data = Image.frombuffer('L', (512,512), data.flatten(), 'raw', 'L', 0, 1)
        key = '{}_{}.png'.format(j, i)
        # print("Inserting: {}".format(key))
        output = six.BytesIO()
        image_data.save(output, format='png'.upper())
        up.queue_task(key, output)
  else:
    for j in range(result.iteration):
      output = six.BytesIO()
      data = np.random.randint(256, size=(512,512), dtype=np.uint8)
      image_data = Image.frombuffer('L', (512,512), data.flatten(), 'raw', 'L', 0, 1)
      image_data.save(output, 'PNG')
      up.queue_task('{}_63.png'.format(j), output)
  
  start_time = time.time()
  for i in range(result.num):
    mp.Process(target=up.worker, args=(up.task_queue,)).start()

  up.task_queue.join()
  up.task_queue.close()

  print ("Time {}".format(time.time()-start_time))

if __name__ == '__main__':
  main()
