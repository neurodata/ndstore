from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class ocpProject ( models.Model):
    token  =  models. CharField(max_length=200)
    description  =  models. CharField(max_length=4096)
    project  =  models. CharField(max_length=200)
    dataset  =  models. CharField(max_length=200)

    DATATYPE_CHOICES = (
        (1, 'Image'),
        (2, 'Annotation'),
        (3, 'Channel 16 bit'),
        (4, 'Channel 8 bit'),
        )
    datatype = models.IntegerField(choices=DATATYPE_CHOICES, default=1)
    

#    dataurl  =  models. CharField(max_length=200)
    resolution = models.IntegerField(default=0)
    READONLY_CHOICES = (
        (1, 'Yes'),
        (0, 'No'),
        )
    readonly =  models.IntegerField(choices=READONLY_CHOICES, default=2)

    EXCEPTION_CHOICES = (
        (1, 'Yes'),
        (0, 'No'),
        )
    exceptions =  models.IntegerField(choices=EXCEPTION_CHOICES, default=2)
    HOST_CHOICES = (
        ('localhost', 'localhost'),
        ('braingraph1.cs.jhu.edu', 'openconnecto.me'),
        ('braingraph1dev.cs.jhu.edu', 'braingraph1dev'),
        ('braingraph2.cs.jhu.edu', 'braingraph2'),
        )
    host =  models.CharField(max_length=200, choices=HOST_CHOICES, default='localhost')
#    NOCREATE_CHOICES = (
 #       (0, 'No'),
 #       (1, 'Yes'),
 #       )
 #   nocreate =  models.IntegerField(choices=NOCREATE_CHOICES, default=0)

    class Meta:
        """ Meta """
        app_label = 'emca'
        db_table = u"projects"
    def __unicode__(self):
        return self.name

# Create your models here.
class ocpDataset ( models.Model):
    dataset  =  models. CharField(max_length=200)    
    ximagesize =  models.IntegerField()
    yimagesize =  models.IntegerField()

    startslice = models.IntegerField()
    endslice = models.IntegerField()
    zoomlevels = models.IntegerField()
    zscale = models.FloatField()
    description  =  models. CharField(max_length=4096)
    
    class Meta:
        """ Meta """
        app_label = 'emca'
        db_table = u"projects"
    def __unicode__(self):
        return self.name
