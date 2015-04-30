__author__ = 'Christian Bianciotto'


from django.db import models
from datetime import datetime


class Deploy(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=10)
    date = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return u'%s - %s' % (self.type, self.date)


class DeployOperation(models.Model):
    FILE_TYPE = (
        ('S', 'Static'),
        ('D', 'Dynamic'),
    )
    OPERATION_TYPE = (
        ('N', 'New'),
        ('NU', 'Not updated'),
        ('U', 'Update'),
        ('R', 'Remove'),
    )

    id = models.AutoField(primary_key=True)
    deploy = models.ForeignKey(Deploy)
    file_type = models.CharField(choices=FILE_TYPE, max_length=2)
    operation_type = models.CharField(choices=OPERATION_TYPE, max_length=2)
    path = models.CharField(max_length=250)
    hash = models.CharField(max_length=128, null=True, blank=True)
    file_stogare = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s | %s' % (self.deploy, self.path)
