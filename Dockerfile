# Use the official Python image as the base image
FROM python:3.11-alpine

# Set the working directory
WORKDIR /usr/src/app

# Copy application code
COPY . .

# Install dependencies and supervisord
RUN apk add --no-cache supervisor \
    && pip install --no-cache-dir -r requirements.txt

# Create a group and user
RUN addgroup -S mygroup && adduser -S myuser -G mygroup

# Change ownership of the application files to the non-root user
RUN chown -R myuser:mygroup /usr/src/app

# Switch to non-root user
USER myuser

# Copy the supervisord configuration
COPY supervisord.conf /etc/supervisord.conf

# Expose the port
EXPOSE 8000

# Set the command to run supervisord
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
