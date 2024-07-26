# Dockerfile
FROM python:3.12

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Run the application
CMD ["gunicorn", "barbing_salon.wsgi:application", "--bind", "0.0.0.0:8000"]
