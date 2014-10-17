from django.db import models

# Create your models here.
class PersonalInfor(models.Model):
  AreaCode = models.CharField(max_length=10)
  PhoneNumber = models.CharField(max_length=10)
  Name = models.CharField(max_length=10)
  City = models.CharField(max_length=10)
  ZIP = models.CharField(max_length=10)
  
  def __unicode__(self):
    return self.AreaCode+' '+self.PhoneNumber+' '+self.Name+' '+self.City+' '+self.ZIP

class GeoInfor(models.Model):
  AreaCode = models.CharField(max_length=10)
  City = models.CharField(max_length=10)
  
  def __unicode__(self):
    return self.AreaCode+' '+self.City

class ZIPList(models.Model):
  ZIP = models.CharField(max_length=10)
  
  def __unicode__(self):
    return self.ZIP
