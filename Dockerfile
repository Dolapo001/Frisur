# Use the official Python image as the base image
FROM python:3.11-alpine

# Set the working directory
WORKDIR /usr/src/app

# Copy application code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a group and user
RUN addgroup -S mygroup && adduser -S myuser -G mygroup

# Change ownership of the application files to the non-root user
RUN chown -R myuser:mygroup /usr/src/app

# Switch to non-root user
USER myuser

# Install docker-compose
RUN apt-get update && apt-get install -y docker-compose

# Make the script executable
RUN chmod +x start.sh


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "0", "barbing_salon.wsgi:application", "./start.sh"]