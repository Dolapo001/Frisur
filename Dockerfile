# Dockerfile
FROM python:3.12

# Set the working directory
WORKDIR /usr/src/app

# Create a non-root user and group
RUN groupadd -r mygroup && useradd -r -g mygroup myuser

# Copy application code
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Switch to the non-root user
USER myuser

# Command to run Celery worker
CMD ["celery", "-A", "barbing_salon", "worker", "--loglevel=info"]
