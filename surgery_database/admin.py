from django.contrib import admin
from .models import Doctor, Patient, Room, Appointment, Surgery, Hospitalization
# Register your models here.
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['doctor_id', 'first_name', 'last_name', 'specialization', 'email', 'phone',
                    'education', 'experience', 'address']
    list_filter = ['specialization', 'last_name', 'first_name']
    search_fields = ['specialization', 'last_name', 'first_name']

class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'first_name', 'last_name', 'gender', 'email', 'phone',
                    'address', 'birth_date', 'blood_type', 'is_hospitalized']
    list_filter = ['address', 'last_name', 'first_name']
    search_fields = ['address', 'phone', 'last_name', 'first_name']

class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'floor', 'beds']
    search_fields = ['room_number']

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'patient_id', 'doctor_id', 'appointment_datetime', 'appointment_status']
    list_filter = ['patient_id', 'doctor_id', 'appointment_datetime', 'appointment_status']
    search_fields = ['appointment_id', 'patient_id', 'doctor_id', 'appointment_datetime', 'appointment_status']

class SurgeryAdmin(admin.ModelAdmin):
    list_display = ['surgery_id', 'appointment_id', 'surgery_datetime', 'surgery_status']
    list_filter = ['surgery_datetime', 'surgery_status']
    search_fields = ['surgery_id', 'appointment_id']

class HospitalizationAdmin(admin.ModelAdmin):
    list_display = ['hospitalization_id', 'patient_id', 'check_in_date', 'check_out_date', 'room_number']
    list_filter = ['patient_id', 'check_in_date', 'check_out_date', 'room_number']
    search_fields = ['patient_id', 'check_in_date', 'check_out_date', 'room_number']

admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Surgery, SurgeryAdmin)
admin.site.register(Hospitalization, HospitalizationAdmin)