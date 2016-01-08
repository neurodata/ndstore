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
  parser = argparse.ArgumentParser(description="Get celery task state")
  parser.add_argument('taskid', action='store', help='Task ID')
  result = parser.parse_args()

  res = celery_app.AsyncResult(result.taskid)
  print res.state

if __name__ == '__main__':
  main()
