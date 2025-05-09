# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies if needed (e.g., for psycopg2)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     postgresql-client \
#     && rm -rf /var/lib/apt/lists/*

#RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

# Install Python dependencies
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Copy project code into the container
COPY . /app/

# Expose the port the app runs on (for Django dev server)
# This is more informational; the actual mapping happens in docker-compose.yml
EXPOSE 8000

# Note: No CMD or ENTRYPOINT here, as it will be provided by docker-compose
# for the web and worker services separately.

# Command to run the Django application using Gunicorn
# The CMD is overridden by the worker container to run celery
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "api.wsgi:application"]

