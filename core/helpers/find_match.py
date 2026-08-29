import os

import cv2
from facial_recon import settings
from core.models import Citizen, Config

_MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml_models')
YUNET_MODEL_PATH = os.path.join(_MODELS_DIR, 'face_detection_yunet_2023mar.onnx')
SFACE_MODEL_PATH = os.path.join(_MODELS_DIR, 'face_recognition_sface_2021dec.onnx')

# Config.maximum_detection_threshold is a 1-99 value (see core/models.py); it
# is interpreted as a percentage and converted to a 0.0-1.0 cosine-similarity
# tolerance below. This default is used when no Config row exists yet.
DEFAULT_MATCH_TOLERANCE = 0.40

_detector = None
_recognizer = None


def _get_detector():
    global _detector
    if _detector is None:
        # YuNet's own default score_threshold (0.9) is tuned for clean,
        # well-lit studio-style photos; real webcam captures (uneven
        # lighting, motion blur, off-angle faces) routinely score below
        # that, so detection silently fails ("Driver Face not detected")
        # even when a face is clearly present. 0.6 is the commonly
        # recommended threshold for in-the-wild capture conditions.
        _detector = cv2.FaceDetectorYN_create(YUNET_MODEL_PATH, "", (320, 320), score_threshold=0.6)
    return _detector


def _get_recognizer():
    global _recognizer
    if _recognizer is None:
        _recognizer = cv2.FaceRecognizerSF_create(SFACE_MODEL_PATH, "")
    return _recognizer


def get_match_tolerance():
    config = Config.objects.first()
    if not config:
        return DEFAULT_MATCH_TOLERANCE
    return config.maximum_detection_threshold / 100.0


def _detect_and_extract_feature(image_path):
    """
    Load an image, detect its (first/largest) face, and return its SFace
    embedding, or None if the image can't be read or has no detectable face.
    """
    image = cv2.imread(image_path)
    if image is None:
        return None

    detector = _get_detector()
    height, width = image.shape[:2]
    detector.setInputSize((width, height))
    _, faces = detector.detect(image)
    if faces is None:
        return None

    recognizer = _get_recognizer()
    aligned_face = recognizer.alignCrop(image, faces[0])
    return recognizer.feature(aligned_face)


def _compare_features(feature1, feature2, tolerance):
    recognizer = _get_recognizer()
    score = float(recognizer.match(feature1, feature2, cv2.FaceRecognizerSF_FR_COSINE))
    return {"status": score >= tolerance, "confidence": score}


def find_face(image_path, tolerance=None):
    """
    Detect the face in image_path and find the closest-matching registered
    citizen.

    Returns None only if no face could be detected in image_path itself.
    Otherwise returns {'driver': Citizen, 'score': float, 'status': bool} for
    the best-scoring citizen - callers MUST check 'status' (True only if the
    score cleared `tolerance`) rather than treating any non-None return as a
    confident match: with citizens registered, this always returns the
    closest one, even if that citizen is a poor/no match.
    """
    if tolerance is None:
        tolerance = get_match_tolerance()

    query_feature = _detect_and_extract_feature(image_path)
    if query_feature is None:
        settings.LOGGER.error('failed to capture face')
        return None

    citizens = Citizen.objects.all().order_by('-pk')
    results = []
    for citizen in citizens:
        settings.LOGGER.debug('checking: {}', citizen)

        if not citizen.picture:
            results.append({'driver': citizen, 'score': 0.0, 'status': False})
            continue

        citizen_feature = _detect_and_extract_feature(citizen.picture.path)
        if citizen_feature is None:
            results.append({'driver': citizen, 'score': 0.0, 'status': False})
            continue

        result = _compare_features(query_feature, citizen_feature, tolerance)
        settings.LOGGER.info(result)
        results.append({'driver': citizen, 'score': result['confidence'], 'status': result['status']})

    # Sort the results based on the score in descending order
    results.sort(key=lambda x: x['score'], reverse=True)

    # Return the driver with the highest score
    settings.LOGGER.debug('sorted list: {}', results)
    if results:
        return results[0]

    else:
        return None


def match_faces(path1: str, path2: str, tolerance: float = None):
    if tolerance is None:
        tolerance = get_match_tolerance()

    feature1 = _detect_and_extract_feature(path1)
    if feature1 is None:
        return {"status": False, "confidence": 0.0, "message": "No face found in new image "}

    feature2 = _detect_and_extract_feature(path2)
    if feature2 is None:
        return {"status": False, "confidence": 0.0, "message": "No face found in existing image "}

    return _compare_features(feature1, feature2, tolerance)
