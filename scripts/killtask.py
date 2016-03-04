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

import sys, os
import argparse

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import django
django.setup()

from OCP import celery_app

def main():
  parser = argparse.ArgumentParser(description="Kill celery task")
  parser.add_argument('taskid', action='store', help='Task ID')
  result = parser.parse_args()

  #res = celery_app.AsyncResult(result.taskid)
  #res.revoke(terminate=True)
  celery_app.control.revoke(result.taskid, terminate=True)

if __name__ == '__main__':
  main()
