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
