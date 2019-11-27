"""surgery_department URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from surgery_database import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),

    #general tables
    path('doctors', views.doctors, name='doctors'),
    path('patients', views.patients, name='patients'),
    path('appointments', views.appointments, name='appointments'),
    path('surgeries', views.surgeries, name='surgeries'),
    path('rooms', views.rooms, name='rooms'),
    path('hospitalization', views.hospitalization, name='hospitalization'),

    #doctors
    path('manage_doctor/<doctor_id>/', views.manage_doctor, name='manage_doctor'),
    path('add_doctor', views.add_doctor, name='add_doctor'),
    path('remove_doctor/<doctor_id>/', views.remove_doctor, name='remove_doctor'),

    # stats
    path('doctor_stats', views.doctor_stats, name='doctor_stats'),
    path('doctor_stats_appointments', views.doctor_stats_appointments, name='doctor_stats_appointments'),
    path('specialization_stats', views.specialization_stats, name='specialization_stats'),

    #patients
    path('manage_patient/<patient_id>/', views.manage_patient, name='manage_patient'),
    path('add_patient', views.add_patient, name='add_patient'),
    path('remove_patient/<patient_id>/', views.remove_patient, name='remove_patient'),

    # appointments
    path('manage_appointment/<appointment_id>/', views.manage_appointment, name='manage_appointment'),
    path('create_appointment', views.create_appointment, name='create_appointment'),
    path('remove_appointment/<appointment_id>/', views.remove_appointment, name='remove_appointment'),

    # surgeries
    path('manage_surgery/<surgery_id>/', views.manage_surgery, name='manage_surgery'),
    path('arrange_surgery', views.arrange_surgery, name='arrange_surgery'),
    path('remove_surgery/<surgery_id>/', views.remove_surgery, name='remove_surgery'),

    # rooms
    path('manage_room/<room_number>/', views.manage_room, name='manage_room'),
    path('add_room', views.add_room, name='add_room'),
    path('remove_room/<room_number>/', views.remove_room, name='remove_room'),

    # hospitalization
    path('manage_hospitalization/<hospitalization_id>/', views.manage_hospitalization, name='manage_hospitalization'),
    path('create_hospitalization', views.create_hospitalization, name='create_hospitalization'),
    path('remove_hospitalization/<hospitalization_id>/', views.remove_hospitalization, name='remove_hospitalization'),
    path('check_out_patient/<hospitalization_id>/', views.check_out_patient, name='check_out_patient'),
    path('hospitalize/<patient_id>/', views.hospitalize, name='hospitalize'),

    # documents
    path('medical_record/<patient_id>/', views.medical_record, name='medical_record'),
    path('death_certificate/<patient_id>/', views.death_certificate, name='death_certificate'),
    path('appointment_certificate/<appointment_id>/', views.appointment_certificate, name='appointment_certificate'),
    path('surgery_certificate/<surgery_id>/', views.surgery_certificate, name='surgery_certificate'),
]
