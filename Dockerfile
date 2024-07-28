

# Use the official Python 3.11 Alpine base image for ARM architecture
FROM python:3.11-alpine

# Install required system dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app




RUN apk add --no-cache tzdata
ENV TZ Europe/London
ENV PYTHONUNBUFFERED=1



# upgrade pip
RUN pip install --upgrade pip


# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn



#RUN pip3 install --upgrade pip setuptools wheel && pip3 install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 80

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
