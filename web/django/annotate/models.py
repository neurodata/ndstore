from django.db import models

# Create your models here.

class Project(models.Model):
  """Annotation project"""
  name = models.CharField(max_length=255)
# TODO make openid a foreign key
  openid = models.CharField(max_length=255)
  token = models.CharField(max_length=255)
  dataset = models.CharField(max_length=255)
  resolution = models.IntegerField()

  def __unicode__(self):
    return self.name
