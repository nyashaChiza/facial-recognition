from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from .models import Citizen, Incident, CitizenImage
from .forms import CitizenSearchForm
from django.db import models
from .forms import CitizenSearchForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Citizen, Incident
from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2
from django.conf import settings
from main import FaceRecognition
import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from .forms import CitizenForm


class IndexView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CitizenSearchForm
        return context


class CitizenListView(ListView):
    model = Citizen
    context_object_name = 'citizens'
    template_name = 'citizens/index.html'
    
    
class CitizenDetailView(DetailView):
    model = Citizen
    context_object_name = 'citizen'
    template_name = 'citizens/detail.html'
    
class IncidentDetailView(DetailView):
    model = Incident
    context_object_name = 'incident'
    template_name = 'incidents/detail.html'
    
class IncidentCreateView(CreateView):
    model = Incident
    fields = '__all__'
    context_object_name = 'incident'
    template_name = 'incidents/create.html'
    
class CitizenCreateView(CreateView):
    model = Citizen
    fields = ['first_name', 'last_name', 'id_type', 'id_number']  # Modify this based on your actual form fields

    def get(self, request, *args, **kwargs):
        citizen_form = CitizenForm()
        return render(request, 'citizens/create.html', {'citizen_form': citizen_form})

    def post(self, request, *args, **kwargs):
        citizen_form = CitizenForm(request.POST)
        if citizen_form.is_valid():
            citizen = citizen_form.save()
            return redirect('home')  # Redirect to a success page or any other page

        return render(request, 'citizens/create.html', {'citizen_form': citizen_form})
   
    
class IncidentListView(ListView):
    model = Incident
    context_object_name = 'incidents'
    template_name = 'incidents/index.html'
    

class ImagesListView(ListView):
    model = CitizenImage
    context_object_name = 'images'
    template_name = 'images/index.html'
    


def search_citizens(request):
    
    citizens = []

    if request.GET:
        search_query = request.GET['search_query']
        citizens = Citizen.objects.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(id_number__icontains=search_query)
        )

    return render(request, 'citizens/search_results.html', {'citizens': citizens})


# views.py


def generate_incident_report(request, citizen_id):
    citizen = get_object_or_404(Citizen, pk=citizen_id)
    incidents = citizen.incidents.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{citizen.first_name} {citizen.last_name} Report.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Add content to the PDF
    p.drawString(100, 800, f"Incident Report for {citizen.first_name} {citizen.last_name}")

    y_position = 780
    for incident in incidents:
        y_position -= 20
        p.drawString(100, y_position, f"Title: {incident.title}")
        y_position -= 15
        p.drawString(100, y_position, f"Comment: {incident.comment}")
        y_position -= 15
        p.drawString(100, y_position, f"Created: {incident.incident_date}")
        y_position -= 15
        p.drawString(100, y_position, "--------------------------------------------")

    # Close the PDF object cleanly, and return the response.
    p.showPage()
    p.save()

    return response




# Import your existing face recognition code here

class VideoCamera:
    def __init__(self):
        self.video_capture = cv2.VideoCapture(0)
        self.face_recognition = FaceRecognition()

    def __del__(self):
        self.video_capture.release()

    def get_frame(self):
        success, frame = self.video_capture.read()
        if success:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rbg_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            settings.LOGGER.critical(len(rbg_small_frame))
            self.face_recognition.run_recognition(rbg_small_frame)

            # Other processing logic as needed

            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def webcam_view(request):
    camera = VideoCamera()
    return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')


from django.shortcuts import render, redirect
from .forms import IncidentForm, CitizenForm, CitizenImageForm

def capture_incident(request):
    if request.method == 'POST':
        incident_form = IncidentForm(request.POST)
        citizen_form = CitizenForm(request.POST)
        image_form = CitizenImageForm(request.POST, request.FILES)

        if incident_form.is_valid() and citizen_form.is_valid() and image_form.is_valid():
            citizen = citizen_form.save()
            incident = incident_form.save(commit=False)
            incident.citizen = citizen
            incident.save()

            image = image_form.save(commit=False)
            image.citizen = citizen
            image.save()

            return redirect('home')  # Redirect to a success page or any other page

    else:
        incident_form = IncidentForm()
        citizen_form = CitizenForm()
        image_form = CitizenImageForm()

    return render(request, 'incidents/create.html', {
        'incident_form': incident_form,
        'citizen_form': citizen_form,
        'image_form': image_form,
    })



import cv2
import base64
import numpy as np
from django.shortcuts import render
from django.http import JsonResponse

def capture_image(request):
    if request.method == 'POST':
        # Get the image data from the POST request
        image_data = request.FILES.get('image_data', None)

        # Process the image data to detect faces
        if image_data:
            # Read image data as byte string
            img_data = image_data.read()

            # Convert byte data to numpy array
            nparr = np.frombuffer(img_data, np.uint8)

            # Decode the image
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Convert image to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            print(gray)
            # Load the pre-trained face detector
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            # Detect faces in the image
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            print(faces)
            if len(faces) > 0:
                # Return the number of faces detected
                return JsonResponse({'num_faces': len(faces)}, status=200)
            else:
                return JsonResponse({'error': 'no face detected'}, status=400)

    # Handle invalid or missing image data
    return JsonResponse({'error': 'Invalid request'}, status=400)

def webcam_view(request):
    return render(request, 'images/create.html')





def capture_driver(request):
    if request.method == 'POST':
        citizen_form = CitizenForm(request.POST)
        if citizen_form.is_valid():
            citizen = citizen_form.save(commit=False)  # Save citizen details
            image_data = request.POST.get('image_data')
            if image_data:
                # Decode base64 image data and save as an image file
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                citizen.picture.save(f'citizen_{citizen.id}.{ext}', ContentFile(base64.b64decode(imgstr)), save=False)
            citizen.save()  # Save the citizen object with the image

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
