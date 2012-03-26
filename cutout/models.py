from django.db import models

# Create your models here.

class Dataset(models.Model):
  """Database configuration for cutout server"""
  name = models.CharField(max_length=255)
  dbuser = models.CharField(max_length=255)
  dbpasswd = models.CharField(max_length=255) 
  dbname = models.CharField(max_length=255) 
  dbhost = models.CharField(max_length=255) 

  def __unicode__(self):
    return self.name
