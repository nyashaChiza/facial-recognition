# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `validate_blacklist_payload`/`validate_citizen_payload` in `core/validators.py`, so the blacklist and edit-driver views reject a malformed request before it reaches form validation.
- `/readiness/` endpoint checking database connectivity, alongside the existing `/health/`.
- Structured (JSON) logging via loguru when `DEBUG=False`.
- CI step verifying the committed ONNX model files aren't LFS/Git pointer stubs.
- Secure cookies and nosniff/frame-deny headers when `DEBUG=False`.
- `has_add_permission` on `ConfigAdmin`, preventing a second `Config` row from being created.

### Fixed
- `generate_incident_report`'s `Content-Disposition` filename could break on a quote or non-ASCII character in a driver's name; it also never paginated, so a driver with more than ~5 incidents had text drawn off the bottom of the PDF.
- `blacklist_citizen` and `reinstate_driver` returned an unhandled 500 for a missing citizen id instead of a 404.

## [0.1.0] - 2026-08-29

Initial tagged release.

### Added
- Driver/citizen registry: register a driver with a photo, ID type, and ID number.
- Face matching against registered drivers using OpenCV's `FaceDetectorYN`/`FaceRecognizerSF` (YuNet + SFace).
- Incident tracking with a points system, logged against the matched driver.
- Auto-blacklisting once a driver's total incident points exceed a configurable threshold.
- Per-driver PDF incident reports.
- Django admin, CI (tests, coverage floor, flake8, pip-audit), and Docker/`docker-compose` support.
