FROM python:3.12-slim

WORKDIR /app

# cmake + build-essential are needed to compile dlib from source (it has no
# prebuilt wheel); libgl1/libglib2.0-0/libsm6/libxext6/libxrender1 are
# runtime needs of opencv-python.
RUN apt-get update && apt-get install -y --no-install-recommends \
    cmake build-essential \
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
