# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies (needed for Postgres and Pillow)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install pymongo==4.6.1

# Copy the Django project
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Default command to run the server
# Default command: Make migrations, apply them, and start the server
CMD sh -c "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"