# Use the official Python image as the base image
FROM python:3.12

# Set the working directory
WORKDIR /usr/src/app

# Copy application code
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Create a group and user
RUN groupadd -r mygroup && useradd -r -g mygroup myuser

# Change ownership of the application files to the non-root user
RUN chown -R myuser:mygroup /usr/src/app

# Switch to non-root user
USER myuser

# Expose the port that the Django application will run on
EXPOSE 8000

# Default command to run Gunicorn for Django
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "barbing_salon.wsgi:application"]
