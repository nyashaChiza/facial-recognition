import face_recognition
from core.models import Citizen
from facial_recon import settings

def compare_faces(image_path):
    # Load the captured image
    captured_image = face_recognition.load_image_file(image_path)

    # Find face locations in the captured image
    captured_face_locations = face_recognition.face_locations(captured_image)

    if not captured_face_locations:
        return None  # No face detected in the captured image

    # Encode the faces in the captured image
    captured_face_encodings = face_recognition.face_encodings(captured_image, captured_face_locations)

    # Get all citizens
    citizens = Citizen.objects.all().order_by('-pk')

    # Loop through all citizens
    for citizen in citizens:
        
        # Get all images associated with the citizen
        citizen_image = citizen.picture
        
        # Loop through all images of the citizen
        if citizen_image:
            # Load the image of the citizen
            citizen_image_data = face_recognition.load_image_file(citizen_image.path)
            citizen_face_encoding = face_recognition.face_encodings(citizen_image_data)

            if citizen_face_encoding:
                # Compare the captured face encoding with the encoding of the citizen's face
                for encoding in citizen_face_encoding:
                    matches = face_recognition.compare_faces(encoding, captured_face_encodings)
                    print(matches)
                    if any(matches):
                        # Match found, return the matched citizen
                        return citizen

    # No match found
    return None
