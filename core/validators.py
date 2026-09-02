class PayloadValidationError(ValueError):
    """Raised when a request payload is missing a required key or has the wrong type."""


def validate_capture_payload(data):
    """
    Check that `data` (a request.POST-like mapping) carries an 'image_data'
    key whose value is a string, before it's handed off to
    decode_captured_image for the actual data-URL/base64 parsing.

    Raises PayloadValidationError if the key is missing or isn't a string
    (e.g. a list, from an unexpected multi-value submission). Returns the
    image_data value on success.
    """
    if 'image_data' not in data:
        raise PayloadValidationError("Missing required field 'image_data'")

    image_data = data.get('image_data')
    if not isinstance(image_data, str):
        raise PayloadValidationError("'image_data' must be a string")

    return image_data
