# Contributing

## Setup

```bash
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
```

## Before opening a PR

Run the test suite and linter, and make sure both are clean:

```bash
python manage.py test
flake8 .
```

CI (`.github/workflows/django.yml`) runs the same checks, plus `pip-audit`,
on every push and PR across Python 3.12-3.14.

## Commit style

- Keep each commit focused on one change, with the tests that pin its
  behavior included in the same commit.
- Avoid bundling unrelated formatting, refactors, and features together.

## Updating dependencies

`requirements.txt` and `requirements-dev.txt` are compiled from
`requirements.in` and `requirements-dev.in` via
[pip-tools](https://pypi.org/project/pip-tools/); see the
[Dependency updates](README.md#dependency-updates) section of the README.
