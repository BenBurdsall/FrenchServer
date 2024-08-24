# Use the official Python 3.11 Alpine base image
FROM python:3.11-alpine

# Install required system dependencies
RUN apk add --no-cache gcc musl-dev

# Set the working directory in the container
WORKDIR /app

RUN mkdir /app/dict
# Copy the current directory contents into the container at /app
COPY . /app
COPY  ./dict /app/dict
# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn  python-multipart starlette itsdangerous starsessions=



ENV TZ Europe/London
ENV PYTHONUNBUFFERED=1



# Make port 8000 available to the world outside this container
EXPOSE 80

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
