FROM python:3.10-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
#COPY flask-app /app/flask-app
COPY flask-app/ .
COPY requirements.txt .
COPY startup.sh .

RUN pip install -r requirements.txt

# Expose Flask port
EXPOSE 5000

#CMD ["python", "flask-app/wsgi.py"]
#CMD ["python", "wsgi.py"]
CMD ["bash", "/app/startup.sh"]



## Use the slim Python 3.10 image as the base to build on
#FROM python:3.10-slim
#
## Copy in the Flask application code
#COPY flask-app/ .
#
## Install the python requirements
#RUN pip install -r requirements.txt
#
## Run the application
#CMD ["python3", "./wsgi.py"]
