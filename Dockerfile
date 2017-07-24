# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Install any needed packages specified in requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Copy the current directory contents into the container at /app
ADD . /app

# Set the working directory to /app
WORKDIR /app

EXPOSE 8888

# Run app.py when the container launches
CMD ["python3", "server.py"]

