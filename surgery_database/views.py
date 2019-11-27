from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, TemplateView
from .models import Doctor, Patient, Appointment, Surgery, Room, Hospitalization
from .forms import DoctorForm, PatientForm, AppointmentForm, SurgeryForm, RoomForm, HospitalizationForm
from django.template.defaulttags import register
from django.contrib import messages
from django.utils import timezone
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

from datetime import date, datetime
from collections import defaultdict
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
# Create your views here.
class HomeView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'index.html')

# ******** TABLE VIEWS ********
def doctors(request):
    doctors = Doctor.objects.all()
    context = {
        'doctors': doctors,
        'specializations': Doctor.SPECIALIZATION_CHOICES,
    }
    return render(request, 'doctors.html', context)

def patients(request):
    patients = Patient.objects.all()
    context = {
        'patients': patients,
        'today': date.today(),
    }
    return render(request, 'patients.html', context)

def appointments(request):
    appointments = Appointment.objects.all()
    context = {
        'appointments': appointments
    }
    return render(request, 'appointments.html', context)

def surgeries(request):
    surgeries = Surgery.objects.all()
    context = {
        'surgeries': surgeries
    }
    return render(request, 'surgeries.html', context)

def rooms(request):
    rooms = Room.objects.all()
    hospitalizations = Hospitalization.objects.all()
    vacant = dict()
    for room in rooms:
        vacant[room.room_number] = room.beds - len(list(Hospitalization.objects.filter(room_number=room)))

    context = {
        'rooms': rooms,
        'vacant': vacant,
        'hospitalizations': hospitalizations
    }

    print(vacant)

    return render(request, 'rooms.html', context)

def hospitalization(request):
    hospitalizations = Hospitalization.objects.all()
    context = {
        'hospitalizations': hospitalizations
    }
    return render(request, 'hospitalization.html', context)

# ********** DOCTOR *********
class DoctorDetailView(DetailView):
    def get(self, *args, **kwargs):
        doctor_id = kwargs['doctor_id']
        print(doctor_id)
        doctor = get_object_or_404(Doctor, doctor_id=doctor_id)

        context = {
            'doctor': doctor
        }

        return render(self.request, 'doctor_details.html', context)

def manage_doctor(request, doctor_id=None):
    if doctor_id:
        doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
    else:
        doctor = None
    if request.method == "POST":
        form = DoctorForm(request.POST or None, instance=doctor)
        if form.is_valid():
            form.save()
            # Do something.
            return redirect('doctors')
        messages.error(request, "Invalid form")
        return redirect('manage_doctor')
    else:
        form = DoctorForm(instance=doctor)

        context = {
            'form': form
        }
        return render(request, 'manage_doctor.html', context)

def add_doctor(request):
    if request.method == "POST":
        form = DoctorForm(request.POST or None)
        if form.is_valid():
            form.save()
            # Do something.
            return redirect('doctors')
        messages.error(request, "Invalid form")
        return redirect('manage_doctor')
    else:
        form = DoctorForm()
        context = {
            'form': form
        }
        return render(request, 'add_doctor.html', context)


def remove_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
    if doctor:
        doctor.delete()
        messages.info(request, f'Doctor with id {doctor_id} was removed from Database')

    return redirect('doctors')

def doctor_stats(request):
    doctors = Doctor.objects.all()
    surgeries = Surgery.objects.all()
    doctors_stats = dict()

    for doctor in doctors:
        statuses = {'S': 0, 'U': 0, 'F': 0, 'C': 0}
        print(doctor)
        surgeries = Surgery.objects.filter(appointment_id__doctor_id= doctor.doctor_id)
        for surgery in surgeries:
            statuses[surgery.surgery_status] += 1
            print(surgery.surgery_status)

        doctors_stats[doctor] = statuses
        print(statuses)

    context = {
        'doctors_stats': doctors_stats,
    }

    return render(request, 'doctor_stats.html', context)

# ******* PATIENT **********
def manage_patient(request, patient_id=None):
    if patient_id:
        patient = get_object_or_404(Patient, patient_id=patient_id)
    else:
        patient = None
    if request.method == "POST":
        form = PatientForm(request.POST or None, instance=patient)
        if form.is_valid():
            form.save()
            # Do something.
            return redirect('patients')
        messages.error(request, "Invalid form")
        return redirect('manage_patient')
    else:
        form = PatientForm(instance=patient)

        context = {
            'form': form
        }
        return render(request, 'manage_patient.html', context)

def add_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST or None)
        if form.is_valid():
            form.save()
            # Do something.
            return redirect('patients')
        messages.error(request, "Invalid form")
        return redirect('add_patient')
    else:
        form = PatientForm()
        context = {
            'form': form
        }
        return render(request, 'add_patient.html', context)

def remove_patient(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    if patient:
        patient.delete()
        messages.info(request, f'Patient with id {patient_id} was removed from Database')

    return redirect('patients')

# ********* APPOINTMENTS ************
def manage_appointment(request, appointment_id=None):
    if appointment_id:
        appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    else:
        appointment = None
    if request.method == "POST":
        form = AppointmentForm(request.POST or None, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointments')
        messages.error(request, "Invalid form")
        return redirect('manage_appointment')
    else:
        form = AppointmentForm(instance=appointment)

        context = {
            'form': form
        }
        return render(request, 'manage_appointment.html', context)

def create_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST or None)
        if form.is_valid():
            if form.cleaned_data['appointment_datetime'] < timezone.now():
                form.cleaned_data['appointment_datetime'] = 'P'
            form.save()
# ЗАДАЧА АВТОМАТИЗАЦИИ: ГОСПИТАЛИЗАЦИЯ ПАЦИЕНТА, ЕСЛИ НА ВРЕМЯ ПОСЕЩЕНИЯ ВРАЧА ОН ЕЩЕ НЕ ГОСПИТАЛИЗИРОВАН
            #patient = get_object_or_404(Patient, patient_id = form.cleaned_data['patient_id'])
            patient = form.cleaned_data['patient_id']
            # check if patient is already hospitalized
            cur_hospitalization = Hospitalization.objects.filter(patient_id=patient.patient_id, check_out_date__isnull=True)
           # if he is not, then we must hospitalize him
            if not cur_hospitalization:
                try:
                    # first check if there are rooms with patients of the dame gender
                    hospitalizations = Hospitalization.objects.filter(patient_id__gender=patient.gender)
                    print("hospitalizations", hospitalizations)
                    # if there are, check if we can allocate patient here
                    if hospitalizations:
                        for hosp in hospitalizations:
                            room = get_object_or_404(Room, room_number=hosp.room_number.room_number)
                            patients_in_room = Hospitalization.objects.filter(room_number=room.room_number)

                            # we can allocate patient in this room, if there are vacant places
                            if room.beds - len(patients_in_room) > 0:
                                today = timezone.now()

                                h = Hospitalization.objects.create(patient_id=patient,
                                            room_number = room)
                                h.save()
                                # allocation was successful
                                messages.info(request,
                                    f"Appointment created. Patient {patient.first_name}{patient.last_name} was"
                                    f"allocated in room {room.room_number}")
                                return redirect('appointments')

                    # else we need to search for vacant rooms
                    rooms = Room.objects.all()
                    for room in rooms:
                        if Hospitalization.objects.filter(room_number = room.room_number).count() == 0:
                            # if room is empty, allocation was successful
                            today = date.today()
                            h = Hospitalization(patient_id=patient.patient_id, check_in_date=today,
                                                room_number=room.room_number)
                            h.save()

                            messages.info(request, f"Appointment created. Patient {patient.first_name}{patient.last_name} was"
                                          f"allocated in room {room.room_number}")
                            return redirect('appointments')

                    #there are no vacant places
                    messages.info(request, f"Appointment created. Patient {patient.first_name}{patient.last_name} "
                                  f"can\'t be allocated in out department, since there are now vacant rooms")
                    return redirect('appointments')

                except:
                    messages.error(request, "Appointment was created, person was not hospitalized. You can hospitalize him in Hospitalization section.")
                    return redirect('appointments')
            # patient is already hospitalized
            else:
                messages.info(request, f"Appointment created. Patient {patient.first_name}{patient.last_name} is already hospitalized")
                return redirect('appointments')

        messages.error(request, "Invalid form")
        return redirect('create_appointment')
    else:
        form = AppointmentForm()
        context = {
            'form': form
        }
        return render(request, 'create_appointment.html', context)

def hospitalize(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    cur_hospitalization = Hospitalization.objects.filter(patient_id=patient.patient_id, check_out_date__isnull=True)
    # if he is not, then we must hospitalize him
    if not cur_hospitalization:
        try:
            # first check if there are rooms with patients of the dame gender
            hospitalizations = Hospitalization.objects.filter(patient_id__gender=patient.gender)
            print("hospitalizations", hospitalizations)
            # if there are, check if we can allocate patient here
            if hospitalizations:
                for hosp in hospitalizations:
                    room = get_object_or_404(Room, room_number=hosp.room_number.room_number)
                    patients_in_room = Hospitalization.objects.filter(room_number=room.room_number)

                    # we can allocate patient in this room, if there are vacant places
                    if room.beds - len(patients_in_room) > 0:
                        today = timezone.now()

                        h = Hospitalization.objects.create(patient_id=patient,
                                                           room_number=room)
                        h.save()
                        # allocation was successful
                        messages.info(request,
                                      f"Patient {patient.first_name}{patient.last_name} was"
                                      f"allocated in room {room.room_number}")
                        return redirect('patients')

            # else we need to search for vacant rooms
            rooms = Room.objects.all()
            for room in rooms:
                if Hospitalization.objects.filter(room_number=room.room_number).count() == 0:
                    # if room is empty, allocation was successful
                    today = date.today()
                    h = Hospitalization(patient_id=patient.patient_id, check_in_date=today,
                                        room_number=room.room_number)
                    h.save()

                    messages.info(request, f"Patient {patient.first_name}{patient.last_name} was"
                    f"allocated in room {room.room_number}")
                    return redirect('patients')

            # there are no vacant places
            messages.info(request, f"Patient {patient.first_name}{patient.last_name} "
            f"can\'t be allocated in out department, since there are now vacant rooms")
            return redirect('patients')

        except:
            messages.error(request,
                           "Person was not hospitalized. You can hospitalize him in Hospitalization section.")
            return redirect('patients')

def remove_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    if appointment:
        appointment.delete()
        messages.info(request, f'Appointment with id {appointment_id} was removed from Database')

    return redirect('appointments')

# ********* SURGERIES ************
def manage_surgery(request, surgery_id=None):
    if surgery_id:
        surgery = get_object_or_404(Surgery, surgery_id=surgery_id)
    else:
        surgery = None
    if request.method == "POST":
        form = SurgeryForm(request.POST or None, instance=surgery)
        if form.is_valid():
            form.save()
            return redirect('surgeries')
        messages.error(request, "Invalid form")
        return redirect('manage_surgery')
    else:
        form = SurgeryForm(instance=surgery)

        context = {
            'form': form
        }
        return render(request, 'manage_surgery.html', context)

def arrange_surgery(request):
    if request.method == "POST":
        form = SurgeryForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('surgeries')
        messages.error(request, "Invalid form")
        return redirect('arrange_surgery')
    else:
        form = SurgeryForm()
        context = {
            'form': form
        }
        return render(request, 'arrange_surgery.html', context)

def remove_surgery(request, surgery_id):
    surgery = get_object_or_404(Surgery, surgery_id=surgery_id)
    if surgery:
        surgery.delete()
        messages.info(request, f'Surgery with id {surgery_id} was removed from Database')

    return redirect('surgeries')

# ****** ROOMS *********
def manage_room(request, room_number=None):
    if room_number:
        room = get_object_or_404(Room, room_number=room_number)
    else:
        room = None
    if request.method == "POST":
        form = RoomForm(request.POST or None, instance=room)
        if form.is_valid():
            form.save()
            return redirect('rooms')
        messages.error(request, "Invalid form")
        return redirect('manage_room')
    else:
        form = RoomForm(instance=room)

        context = {
            'form': form
        }
        return render(request, 'manage_room.html', context)

def add_room(request):
    if request.method == "POST":
        form = RoomForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('rooms')
        messages.error(request, "Invalid form")
        return redirect('add_room')
    else:
        form = RoomForm()
        context = {
            'form': form
        }
        return render(request, 'add_room.html', context)

def remove_room(request, room_number):
    room = get_object_or_404(Room, room_number=room_number)
    if room:
        room.delete()
        messages.info(request, f'Room with number {room_number} was removed from Database')

    return redirect('surgeries')

# ****** HOSPITALIZATION *********
def check_out_patient(request, hospitalization_id):
    hosp = get_object_or_404(Hospitalization, hospitalization_id=hospitalization_id)
    hosp.check_out_date = date.today()
    hosp.save()
    messages.info(request, f"Patient {hosp.patient_id.last_name} {hosp.patient_id.first_name} was checked out")
    return redirect('hospitalization')

def manage_hospitalization(request, hospitalization_id=None):
    if hospitalization_id:
        hospitalization = get_object_or_404(Hospitalization, hospitalization_id=hospitalization_id)
    else:
        hospitalization = None
    if request.method == "POST":
        form = HospitalizationForm(request.POST or None, instance=hospitalization)
        if form.is_valid():
            form.save()
            return redirect('hospitalization')
        messages.error(request, "Invalid form")
        return redirect('manage_hospitalization')
    else:
        form = HospitalizationForm(instance=hospitalization)

        context = {
            'form': form
        }
        return render(request, 'manage_hospitalization.html', context)

def create_hospitalization(request):
    if request.method == "POST":
        form = HospitalizationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('hospitalization')
        messages.error(request, "Invalid form")
        return redirect('create_hospitalization')
    else:
        form = HospitalizationForm()
        context = {
            'form': form
        }
        return render(request, 'create_hospitalization.html', context)

def remove_hospitalization(request, hospitalization_id):
    hospitalization = get_object_or_404(Hospitalization, hospitalization_id=hospitalization_id)
    if hospitalization:
        hospitalization.delete()
        messages.info(request, f'Hospitalization with id {hospitalization_id} was removed from Database')

    return redirect('hospitalization')

# ****** DOCUMENTS *******
def medical_record(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)

    textobject = p.beginText()
    textobject.setTextOrigin(50, 800)
    textobject.setFont('Times-Roman', 20)

    textobject.textLine(text='MEDICAL CERTIFICATE')
    textobject.textLine(text=f"Name: {patient.last_name} {patient.first_name}")
    textobject.textLine(text=f"Gender: {patient.gender}")
    textobject.textLine(text=f"Date of birth: {patient.birth_date}")
    if patient.death_date:
        textobject.textLine(text=f"Date of death: {patient.death_date}")
    textobject.textLine(text=f"Address: {patient.address}")
    textobject.textLine(text=f"Phone number: {patient.phone}")
    textobject.textLine(text=f"E-mail: {patient.email}")
    textobject.textLine(text=f"Blood type: {patient.blood_type}")

    textobject.textLine(text="")
    today = date.today()
    textobject.textLine(text=f"Certificate made on: {today}")

    p.drawText(textobject)

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'medical_record_{patient.last_name}_{patient.first_name}.pdf')

def death_certificate(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    surgery = get_object_or_404(Surgery, appointment_id__patient_id= patient_id, surgery_status='U')

    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)

    textobject = p.beginText()
    textobject.setTextOrigin(50, 800)
    textobject.setFont('Times-Roman', 20)

    textobject.textLine(text='DEATH CERTIFICATE')
    textobject.textLine(text=f"Name: {patient.last_name} {patient.first_name}")
    textobject.textLine(text=f"Address: {patient.address}")
    textobject.textLine(text=f"Gender: {patient.gender}")
    textobject.textLine(text=f"Who was born on: {patient.birth_date}")
    textobject.textLine(text=f"Had died on: {patient.death_date}")
    if surgery:
        textobject.textLine(text=f"Because of: {surgery.appointment_id.doctor_id.get_specialization_display()} surgery")

    textobject.textLine(text="")
    today = date.today()
    textobject.textLine(text=f"Certificate made on: {today}")

    p.drawText(textobject)

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'death_certificate_{patient.last_name}_{patient.first_name}.pdf')

def appointment_certificate(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)

    textobject = p.beginText()
    textobject.setTextOrigin(25, 800)
    textobject.setFont('Times-Roman', 15)

    textobject.textLine(text='APPOINTMENT CERTIFICATE')
    textobject.textLine(text=f"Patient {appointment.patient_id.last_name} {appointment.patient_id.first_name}")
    textobject.textLine(text=f"Gender: {appointment.patient_id.gender}")
    textobject.textLine(text=f"Date of birth: {appointment.patient_id.birth_date}")
    textobject.textLine(text=f"Address: {appointment.patient_id.address}")
    textobject.textLine(text="")
    textobject.textLine(text=f"Visited: {appointment.doctor_id.last_name} {appointment.doctor_id.first_name}")
    textobject.textLine(text=f"Specialization: {appointment.doctor_id.get_specialization_display()}")
    textobject.textLine(text=f"Diagnosis: {appointment.diagnosis}")
    textobject.textLine(text=f"Prescribtion: {appointment.prescribtion}")

    textobject.textLine(text="")
    today = date.today()
    textobject.textLine(text=f"Certificate made on: {today}")

    p.drawText(textobject)

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True,
                        filename=f'appointment_certificate_{appointment.patient_id.last_name}_{appointment.patient_id.first_name}_{appointment.appointment_datetime}.pdf')

def surgery_certificate(request, surgery_id):
    surgery = get_object_or_404(Surgery, surgery_id=surgery_id)
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)

    textobject = p.beginText()
    textobject.setTextOrigin(25, 800)
    textobject.setFont('Times-Roman', 15)

    textobject.textLine(text='SURGERY CERTIFICATE')
    textobject.textLine(text=f"Patient {surgery.appointment_id.patient_id.last_name} {surgery.appointment_id.patient_id.first_name}")
    textobject.textLine(text=f"Gender: {surgery.appointment_id.patient_id.gender}")
    textobject.textLine(text=f"Date of birth: {surgery.appointment_id.patient_id.birth_date}")
    textobject.textLine(text=f"Address: {surgery.appointment_id.patient_id.address}")
    textobject.textLine(text="")
    textobject.textLine(text=f"Was on surgery carried out by: {surgery.appointment_id.doctor_id.last_name} {surgery.appointment_id.doctor_id.first_name}")
    textobject.textLine(text=f"Specialization: {surgery.appointment_id.doctor_id.get_specialization_display()}")
    textobject.textLine(text=f"Because of: {surgery.appointment_id.diagnosis}")
    textobject.textLine(text=f"Surgery made on: {surgery.surgery_datetime}")
    textobject.textLine(text=f"Status: {surgery.get_surgery_status_display()}")

    textobject.textLine(text="")
    today = date.today()
    textobject.textLine(text=f"Certificate made on: {today}")

    p.drawText(textobject)

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True,
                        filename=f'surgery_certificate_{surgery.appointment_id.patient_id.last_name}_{surgery.appointment_id.patient_id.first_name}_{surgery.surgery_datetime}.pdf')

def doctor_stats_appointments(request):
    doctors = Doctor.objects.all()
    doctors_stats = dict()

    for doctor in doctors:
        appointments = Appointment.objects.filter(doctor_id=doctor.doctor_id)
        doctors_stats[doctor] = len(appointments)

    context = {
        'doctors_stats': doctors_stats,
    }

    return render(request, 'doctor_stats_appointments.html', context)
# NOT WORKING!!!!!!
def specialization_stats(request):
    doctors = Doctor.objects.all()
    app_stats = dict()
    sur_stats = dict()
    specializations = Doctor.SPECIALIZATION_CHOICES
    specs = []
    for spec in specializations:
        specs.append(spec[1])
        app_stats[spec[1]] = 0
        sur_stats[spec[1]] = 0
    print(specs)

    for doctor in doctors:
        print('DOCTOR', doctor.get_specialization_display())
        appointments = Appointment.objects.filter(doctor_id=doctor.doctor_id)
        surgeries = Surgery.objects.filter(appointment_id__doctor_id=doctor.doctor_id)
        cur_spec = doctor.get_specialization_display()
        app_stats[cur_spec] += len(appointments)
        print(doctor.get_specialization_display)
        print("STAAAAAAAAAAAATS",app_stats[cur_spec])
        sur_stats[cur_spec] += len(surgeries)
    print('aaa', app_stats)
    print('sss', sur_stats)

    context = {
        'app_stats': app_stats,
        'sur_stats': sur_stats,
        'specs': specs,
    }

    return render(request, 'specialization_stats.html', context)