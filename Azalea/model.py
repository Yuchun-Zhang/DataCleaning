from django.db import models

class PersonalInfo(models.Model):
  AeraCode = models.CharField(max_length=10)
  PhoneName = models.CharField(max_length=10)
  Name = models.CharField(max_length=10)
  City = models.CharField(max_length=10)
  ZIP = models.CharField(max_length=10)

class GeoInfor(models.Model):
  AeraCode = models.CharField(max_length=10)
  City = models.CharField(max_length=10)

class ZIPList(models.Model):
  ZIP = models.CharField(max_length=10)
