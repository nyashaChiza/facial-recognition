import face_recognition
from core.models import Citizen
from facial_recon import settings

def find_face(image_path):
    captured_image = face_recognition.load_image_file(image_path)
    captured_face_locations = face_recognition.face_locations(captured_image)

    if not captured_face_locations:
        return None

    citizens = Citizen.objects.all().order_by('-pk')
    results = []
    for citizen in citizens:
        citizen_image_path = citizen.picture.path
        settings.LOGGER.debug(f'checking: {citizen}')
        result = match_faces(image_path, citizen_image_path)
        settings.LOGGER.info(result)
        results.append({'driver': citizen, 'score': result['confidence']})

    # Sort the results based on the score in descending order
    results.sort(key=lambda x: x['score'], reverse=True)

    # Return the driver with the highest score
    if results:
        return results[0]['driver']
    else:
        return None

def match_faces(path1: str, path2: str, tolerance: float = 0.8):
    image1 = face_recognition.load_image_file(path1)
    image2 = face_recognition.load_image_file(path2)

    face_encodings1 = face_recognition.face_encodings(image1)
    face_encodings2 = face_recognition.face_encodings(image2)

    if not face_encodings1:
        return {"status": False, "confidence": 0.0, "message": "No face found in image 1"}
    if not face_encodings2:
        return {"status": False, "confidence": 0.0, "message": "No face found in image 2"}

    max_confidence = 0.0
    for encoding1 in face_encodings1:
        for encoding2 in face_encodings2:
            # Compare face encodings and calculate confidence
            confidence = 1 - face_recognition.face_distance([encoding1], encoding2)[0]
            max_confidence = max(max_confidence, confidence)

    # Determine match status based on maximum confidence
    status = max_confidence >= tolerance

    return {"status": status, "confidence": max_confidence}
