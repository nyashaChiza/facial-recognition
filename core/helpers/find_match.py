import face_recognition
from core.models import Citizen
from facial_recon import settings

def find_face(image_path, tolarence = 0.6):
    captured_image = face_recognition.load_image_file(image_path)
    captured_face_locations = face_recognition.face_locations(captured_image)

    if not captured_face_locations:
        settings.LOGGER.error(f'failed to capture face')
        return None

    citizens = Citizen.objects.all().order_by('-pk')
    results = []
    for citizen in citizens:
        citizen_image_path = citizen.picture.path
        settings.LOGGER.debug(f'checking: {citizen}')
        result = match_faces(image_path, citizen_image_path, tolarence)
        settings.LOGGER.info(result)
        results.append({'driver': citizen, 'score': result['confidence'], 'status': result["status"]})

    # Sort the results based on the score in descending order
    results.sort(key=lambda x: x['score'], reverse=True)

    # Return the driver with the highest score
    settings.LOGGER.debug(f'sorted list: {results}')
    if results :
        return results[0]

    else:
        return None

def match_faces(path1: str, path2: str, tolerance: float = 0.75):
    image1 = face_recognition.load_image_file(path1)
    image2 = face_recognition.load_image_file(path2)

    face_encodings1 = face_recognition.face_encodings(image1)
    face_encodings2 = face_recognition.face_encodings(image2)

    if not face_encodings1:
        return {"status": False, "confidence": 0.0, "message": "No face found in new image "}
    if not face_encodings2:
        return {"status": False, "confidence": 0.0, "message": "No face found in existing image "}

    max_confidence = 0.0
    for encoding1 in face_encodings1:
        # Compare face encoding from image1 with all face encodings from image2
        distances = face_recognition.face_distance(face_encodings2, encoding1)
        # Find the minimum distance (maximum similarity) among all comparisons
        min_distance = min(distances)
        # Calculate confidence based on the minimum distance
        confidence = 1 - min_distance
        # Update max_confidence if the new confidence is higher
        max_confidence = max(max_confidence, confidence)

    # Determine match status based on maximum confidence
    status = max_confidence >= tolerance

    return {"status": status, "confidence": max_confidence}
