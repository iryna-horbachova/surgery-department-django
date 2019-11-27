# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
import datetime


class Appointment(models.Model):
    STATUS_CHOICES = [('P', 'Past'), ('F', 'Forthcoming')]
    appointment_id = models.AutoField(primary_key=True)
    patient_id = models.ForeignKey('Patient', db_column='patient_id', on_delete=models.CASCADE, blank=False, null=False)
    doctor_id = models.ForeignKey('Doctor', db_column='doctor_id', on_delete=models.CASCADE, blank=False, null=False)
    appointment_datetime = models.DateTimeField(blank=False, null=False)
    appointment_status = models.CharField(choices=STATUS_CHOICES, max_length=17, default='F', blank=False, null=False)
    diagnosis = models.CharField(max_length=100, blank=True, null=True)
    prescribtion = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'appointments'

    def __str__(self):
        return f"Appointment # {self.appointment_id} made by {self.doctor_id.first_name} {self.doctor_id.last_name} on {self.patient_id.first_name} {self.patient_id.last_name} at {self.appointment_datetime}"


class Doctor(models.Model):
    GENDER_CHOICES = [('F', 'Female'), ('M', 'Male')]
    SPECIALIZATION_CHOICES = [('CR', 'Colon and Rectal Surgery'), ('G', 'General Surgery'), ('T', 'Thoracic Surgery'), ('N', 'Neurological Surgery')]
    doctor_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=70, blank=False, null=False)
    last_name = models.CharField(max_length=70, blank=False, null=False)
    gender = models.CharField(choices= GENDER_CHOICES, max_length=15, blank=False, null=False)
    specialization = models.CharField(choices= SPECIALIZATION_CHOICES, max_length=50, blank=False, null=False)
    email = models.CharField(max_length=50, blank=False, null=False)
    phone = models.IntegerField(blank=False, null=False)
    education = models.CharField(max_length=40, blank=False, null=False)
    experience = models.IntegerField(blank=False, null=False)
    birth_date = models.DateField(blank=False, null=False)
    address = models.CharField(max_length=50, blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'doctors'

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.specialization}, {self.phone}"


class Hospitalization(models.Model):
    hospitalization_id = models.AutoField(primary_key=True)
    patient_id = models.ForeignKey('Patient', db_column='patient_id', on_delete=models.CASCADE, blank=False, null=False)
    check_in_date = models.DateField(default=datetime.date.today, blank=False, null=False)
    check_out_date = models.DateField(blank=True, null=True)
    room_number = models.ForeignKey('Room', on_delete=models.CASCADE, db_column='room_number', blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'hospitalization'

    def __str__(self):
        return f"Hospitalization # {self.hospitalization_id} of {self.patient_id.first_name} {self.patient_id.last_name} on {self.check_in_date} in room {self.room_number.room_number}"


class Patient(models.Model):
    GENDER_CHOICES = [('F', 'Female'), ('M', 'Male')]
    BLOOD_CHOICES = [('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')]
    patient_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=70, blank=False, null=False)
    last_name = models.CharField(max_length=70, blank=False, null=False)
    is_hospitalized = models.BooleanField(default=False, blank=False, null=False)
    gender = models.CharField(choices=GENDER_CHOICES,max_length=17, blank=False, null=False)
    email = models.CharField(max_length=50, blank=False, null=False)
    phone = models.IntegerField(blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
    birth_date = models.DateField(blank=False, null=False)
    death_date = models.DateField(blank=True, null=True)
    blood_type = models.CharField(choices=BLOOD_CHOICES, max_length=17, blank=False, null=False)


    class Meta:
        managed = True
        db_table = 'patients'

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.address}, {self.phone}"


class Room(models.Model):
    room_number = models.IntegerField(primary_key=True)
    floor = models.IntegerField(blank=False, null=False)
    beds = models.IntegerField(blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'rooms'

    def __str__(self):
        return f"Room number {self.room_number} with {self.beds} on {self.floor} floor"


class Surgery(models.Model):
    STATUS_CHOICES = [('S', 'Successful'), ('U', 'Unsuccessful'), ('F', 'Forthcoming')]
    surgery_id = models.AutoField(primary_key=True)
    appointment_id = models.ForeignKey('Appointment', on_delete=models.CASCADE, db_column='appointment_id', blank=False, null=False)
    surgery_datetime = models.DateTimeField(blank=False, null=False)
    surgery_status = models.CharField(choices=STATUS_CHOICES, max_length=20, blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'surgeries'

    def __str__(self):
        return f"Surgery # {self.surgery_id} made by {self.appointment_id.doctor_id.first_name} {self.appointment_id.doctor_id.last_name} on {self.appointment_id.patient_id.first_name} {self.appointment_id.patient_id.last_name} at {self.surgery_datetime}"
