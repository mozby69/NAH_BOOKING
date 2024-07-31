from django.db import models

# Create your models here.
class Event_booking(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200,null=True,blank=True)
    start_time = models.CharField(max_length=200,null=True,blank=True)
    end_time = models.CharField(max_length=200,null=True,blank=True)
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=200,null=True,blank=True)
    contactnumber = models.CharField(max_length=200,null=True,blank=True)
    numberofpersons = models.CharField(max_length=200,null=True,blank=True)
    reservationdate = models.DateField(null=True,blank=True)

    class Meta:
         db_table = "event_booking"