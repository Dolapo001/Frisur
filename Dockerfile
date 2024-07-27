FROM python:3

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /usr/src/app

# Copy requirements file
COPY requirements.txt ./

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .


# Copy the entrypoint script
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh


# Expose the port the app runs on
EXPOSE 8000

# Command to run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "barbing_salon.wsgi:application"]
