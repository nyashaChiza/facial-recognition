import os
import base64
import binascii

from loguru import logger
from django.core.files.base import ContentFile

from core.helpers import find_face
from core.models import Citizen

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB


class InvalidImageDataError(ValueError):
    """Raised when captured image_data is missing, malformed, or too large."""


def decode_captured_image(image_data):
    """
    Validate and decode a data-URL-style base64 image string, e.g.
    "data:image/png;base64,....". Returns (ext, decoded_bytes).
    """
    if not image_data or not image_data.startswith('data:image/'):
        raise InvalidImageDataError('Missing or invalid image data')

    try:
        header, imgstr = image_data.split(';base64,')
    except ValueError:
        raise InvalidImageDataError('Malformed image data')

    ext = header.split('/')[-1]

    try:
        decoded = base64.b64decode(imgstr, validate=True)
    except (binascii.Error, ValueError):
        raise InvalidImageDataError('Could not decode image data')

    if len(decoded) > MAX_IMAGE_BYTES:
        raise InvalidImageDataError(f'Image exceeds the {MAX_IMAGE_BYTES // (1024 * 1024)}MB size limit')

    return ext, decoded


def write_temp_image(decoded_bytes, ext):
    temp_image_path = f'temp_image.{ext}'
    with open(temp_image_path, 'wb') as f:
        f.write(decoded_bytes)
    return temp_image_path


def process_driver_capture(citizen, image_data):
    """
    Decode a captured image, check it against registered drivers, and
    either save it against `citizen` or report a duplicate-face match.

    Returns {"status": "saved" | "duplicate", "detection": dict | None}.
    Raises InvalidImageDataError if image_data is missing/malformed/too large.
    """
    ext, decoded = decode_captured_image(image_data)
    temp_image_path = write_temp_image(decoded, ext)
    try:
        detection = find_face(temp_image_path)
    finally:
        os.remove(temp_image_path)

    logger.info(detection)

    if detection and detection.get('status'):
        return {"status": "duplicate", "detection": detection}

    citizen.picture.save(f'citizen_{citizen}.{ext}', ContentFile(decoded), save=False)
    citizen.save()
    return {"status": "saved", "detection": detection}


def reinstate_driver(citizen_id):
    """Clear a citizen's blacklist status and reason. Returns the citizen."""
    citizen = Citizen.objects.get(pk=citizen_id)
    citizen.is_blacklisted = False
    citizen.blacklist_reason = ""
    citizen.save()
    return citizen
