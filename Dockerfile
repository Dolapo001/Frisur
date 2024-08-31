# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install docker-compose
RUN apt-get update && apt-get install -y docker-compose

# Make the script executable
RUN chmod +x start.sh

# Run the script
CMD ["./start.sh"]
