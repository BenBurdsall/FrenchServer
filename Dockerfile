FROM python:3.10-rc-alpine3.12





# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.12/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.12/community" >> /etc/apk/repositories

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

RUN pip3 install --upgrade pip setuptools wheel && pip3 install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 80

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
