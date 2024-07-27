# Dockerfile
FROM python:3.12

# Create a user with a specific UID and GID
RUN groupadd -g 1001 mygroup && useradd -m -u 1001 -g mygroup myuser

# Set the working directory
WORKDIR /app

# Copy application code
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Switch to non-root user
USER myuser

# Entry point for your application
ENTRYPOINT ["gunicorn", "myapp.wsgi:application"]
