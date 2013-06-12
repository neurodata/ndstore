from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class ocpProject ( models.Model):
    #user  =  models.OneToOneField(User)
    token  =  models. CharField(max_length=200)
    #openid  =  models. CharField(max_length=200,default=User, editable=False)
#    openid  =   models.OneToOneField(User)
    host  =  models. CharField(max_length=200)
    project  =  models. CharField(max_length=200)
    dataset  =  models. CharField(max_length=200)

    DATATYPE_CHOICES = (
        (1, 'Image'),
        (2, 'Annotation'),
        )
    datatype = models.IntegerField(choices=DATATYPE_CHOICES, default=1)
    

    dataurl  =  models. CharField(max_length=200)
    READONLY_CHOICES = (
        (1, 'Yes'),
        (2, 'No'),
        )
    readonly =  models.IntegerField(choices=READONLY_CHOICES, default=2)

    EXCEPTION_CHOICES = (
        (1, 'Yes'),
        (2, 'No'),
        )
    exceptions =  models.IntegerField(choices=EXCEPTION_CHOICES, default=2)
    NOCREATE_CHOICES = (
        (0, 'No'),
        (1, 'Yes'),
        )
    nocreate =  models.IntegerField(choices=NOCREATE_CHOICES, default=0)
    class Meta:
        """ Meta """
        app_label = 'emca'
        db_table = u"projects"
    def __unicode__(self):
        return self.name

# Create your models here.
