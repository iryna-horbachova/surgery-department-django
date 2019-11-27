from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from .models import Doctor, Patient, Appointment, Surgery, Room, Hospitalization

class DoctorForm(ModelForm):
    #gender = forms.ChoiceField(choices=Doctor.GENDER_CHOICES)
    class Meta:
        model = Doctor
        fields = ['doctor_id', 'first_name', 'last_name', 'gender', 'specialization', 'email',
                  'phone', 'education', 'experience', 'birth_date', 'address']

        widgets = {
            'gender': forms.Select(choices=Doctor.GENDER_CHOICES),
            'specialization': forms.Select(choices=Doctor.SPECIALIZATION_CHOICES)
        }

class PatientForm(ModelForm):
    class Meta:
        model = Patient
        fields = ['patient_id', 'first_name', 'last_name', 'gender', 'blood_type',
                  'phone', 'birth_date', 'death_date', 'address', 'email']

        required = ['patient_id', 'first_name', 'last_name', 'gender', 'blood_type',
                  'phone', 'birth_date', 'address', 'email']

        widgets = {
            'gender': forms.Select(choices=Patient.GENDER_CHOICES),
            'blood_type': forms.Select(choices=Patient.BLOOD_CHOICES),
        }

        labels = {
            'blood_type': _('Blood type'),
        }

class AppointmentForm(ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_id', 'patient_id', 'doctor_id', 'appointment_datetime', 'appointment_status', 'diagnosis',
                  'prescribtion']

        widgets = {
            'patient_id': forms.Select(choices=Patient.objects.all()),
            'appointment_status': forms.Select(choices=Appointment.STATUS_CHOICES),
        }

class SurgeryForm(ModelForm):
    class Meta:
        model = Surgery
        fields = ['appointment_id', 'surgery_id', 'surgery_datetime', 'surgery_status']

        widgets = {
            'appointment_id': forms.Select(choices=Appointment.objects.all()),
            'surgery_status': forms.Select(choices=Surgery.STATUS_CHOICES),
        }

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'floor', 'beds']

def not_hospitalized():
    not_hospitalized = []
    result = []
    patients = Patient.objects.all()
    print(patients)
    #hospitalizations = Hospitalization.objects.all()
    for patient in patients:
        hospitalization= Hospitalization.objects.filter(patient_id=patient, check_out_date__isnull=True)
        print('hospitalization', hospitalization)
        if not hospitalization:
            not_hospitalized.append(patient)
    print('NOT', not_hospitalized)

    for patient in not_hospitalized:
        result.append((patient, patient))
    print('RESULT', result)
    return result

class HospitalizationForm(ModelForm):
    class Meta:
        model = Hospitalization
        fields = ['hospitalization_id', 'patient_id', 'check_in_date', 'check_out_date', 'room_number']

        widgets = {
            'patient_id': forms.Select(choices=not_hospitalized()),
        }
