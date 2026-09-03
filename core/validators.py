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


def validate_required_fields(data, fields):
    """
    Check that `data` (a request.POST-like mapping) has each name in
    `fields` present and holding a string value, before it's handed to a
    Django form. Raises PayloadValidationError naming the first missing or
    wrong-typed field.
    """
    for field in fields:
        if field not in data:
            raise PayloadValidationError(f"Missing required field '{field}'")
        if not isinstance(data.get(field), str):
            raise PayloadValidationError(f"'{field}' must be a string")


def validate_blacklist_payload(data):
    """Required fields for the blacklist_citizen view's POST body."""
    validate_required_fields(data, ['blacklist_reason'])


def validate_citizen_payload(data):
    """Required fields for CitizenForm, as posted by the edit_citizen view."""
    validate_required_fields(data, ['first_name', 'last_name', 'id_type', 'id_number'])
