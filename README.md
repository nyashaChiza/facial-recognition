# Face Recognition and Image Comparison

A Django app for managing a driver/citizen registry with face-recognition-based
identity verification: capture a driver's photo on registration, match a
photo captured at an incident against registered drivers using the
`face_recognition` library, log incidents, and auto-blacklist drivers whose
incident points exceed a configurable threshold.

## Features
- **Driver registry:** register citizens/drivers with a photo, ID type and ID number.
- **Face matching:** compares a captured photo against registered drivers via `face_recognition`.
- **Incident tracking:** log incidents against a matched driver, with a points system.
- **Auto-blacklisting:** a driver is automatically blacklisted once their total incident points exceed a configurable threshold (see System Settings in the app).
- **PDF reports:** generate a per-driver incident report as a PDF.

## Prerequisites
- Python 3.12+
- `cmake` and a C/C++ compiler (needed to build `dlib`, which `face_recognition`
  depends on and which has no prebuilt wheel on most platforms). On Debian/Ubuntu:
  `sudo apt-get install cmake build-essential`. On Windows, install Visual
  Studio Build Tools (C++ workload) and CMake.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/nyashaChiza/facial-recognition.git
   cd facial-recognition
   ```
2. Install dependencies (this compiles `dlib` and can take several minutes):
   ```bash
   pip install -r requirements.txt
   ```
   For local development (tests, linting), install the dev dependencies instead:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   - `SECRET_KEY`: Django secret key. Any value works locally; use a real
     random value in production.
   - `DEBUG`: `True` for local development, `False` in production.
   - `ALLOWED_HOSTS`: comma-separated hostnames Django will serve.
   - `CSRF_TRUSTED_ORIGINS`: only needed when exposing the dev server through
     a tunnel (e.g. ngrok).
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
   This also seeds a default `Config` row (detection/points thresholds),
   which the app requires to exist.
5. Run the application:
   ```bash
   python manage.py runserver
   ```

### Running with Docker

```bash
docker build -t facial-recognition .
docker run --env-file .env -p 8000:8000 facial-recognition
```

## Usage
1. Open `localhost:8000` in your browser.
2. Register a driver with a photo under "Drivers".
3. Capture an incident photo; the app matches it against registered drivers
   and logs the incident against the matched driver.
4. Adjust detection/points thresholds under "System Settings".

## Testing

```bash
pip install -r requirements-dev.txt
python manage.py test
```

## Linting

```bash
flake8 .
```

CI runs both the test suite and flake8 on every push/PR.

## Dependency updates

`requirements.txt` and `requirements-dev.txt` are the pinned, installable lockfiles. `requirements.in` and `requirements-dev.in` list the direct dependencies they were compiled from (via [pip-tools](https://pypi.org/project/pip-tools/)):

```bash
pip install pip-tools
pip-compile requirements.in
pip-compile requirements-dev.in
```

[Dependabot](.github/dependabot.yml) opens a weekly PR for outdated pip and GitHub Actions dependencies.

## Important Note
- This is a basic example; real-world applications may require additional security measures, compliance with privacy laws, and more advanced image processing techniques.
