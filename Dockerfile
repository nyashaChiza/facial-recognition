FROM python:3.12-slim

WORKDIR /app

# Runtime libs opencv-python needs to import cv2. No compiler needed here -
# every dependency in requirements.txt ships a prebuilt wheel.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY manage.py .
COPY core/ core/
COPY facial_recon/ facial_recon/
COPY templates/ templates/

ENV DEBUG=False

EXPOSE 8000

CMD ["gunicorn", "facial_recon.wsgi:application", "--bind", "0.0.0.0:8000"]
