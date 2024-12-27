# File: OCR/Dockerfile

# Step 1: Use the latest Python 3.11 slim base image
FROM python:3.11-slim

# Step 2: Set environment variables to prevent .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Step 3: Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Step 4: Set the working directory
WORKDIR /app

# Step 5: Copy the application files
COPY . /app

# Step 6: Install the latest pip version and Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Step 7: Expose the application port
EXPOSE 5000

# Step 8: Command to run the Flask app
CMD ["python", "app.py"]
