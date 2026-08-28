# Face Recognition and Image Comparison

A Django app for managing a driver/citizen registry with face-recognition-based
identity verification: capture a driver's photo on registration, match a
photo captured at an incident against registered drivers using OpenCV's
`FaceDetectorYN`/`FaceRecognizerSF` (YuNet + SFace), log incidents, and
auto-blacklist drivers whose incident points exceed a configurable threshold.

## Features
- **Driver registry:** register citizens/drivers with a photo, ID type and ID number.
- **Face matching:** compares a captured photo against registered drivers using OpenCV's built-in face detection/recognition models (see `core/ml_models/`).
- **Incident tracking:** log incidents against a matched driver, with a points system.
- **Auto-blacklisting:** a driver is automatically blacklisted once their total incident points exceed a configurable threshold (see System Settings in the app).
- **PDF reports:** generate a per-driver incident report as a PDF.

## Prerequisites
- Python 3.12 or newer (this project has no dependency that needs compiling
  from source - every package in `requirements.txt` ships a prebuilt wheel,
  including on brand-new Python releases, so no C/C++ compiler or CMake is
  needed).

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/nyashaChiza/facial-recognition.git
   cd facial-recognition
   ```
2. Install dependencies:
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

To check coverage (CI enforces a 70% floor, configured in `.coveragerc`):

```bash
coverage run manage.py test
coverage report
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

[Dependabot](.github/dependabot.yml) opens a weekly PR for outdated pip and GitHub Actions dependencies. CI also runs [`pip-audit`](https://pypi.org/project/pip-audit/) against `requirements.txt` on every push/PR to catch known vulnerabilities:

```bash
pip install pip-audit
pip-audit -r requirements.txt --desc
```

## Important Note
- This is a basic example; real-world applications may require additional security measures, compliance with privacy laws, and more advanced image processing techniques.
