# Start with the python:3.12 image (temporary; P33 replaces this Dockerfile)
FROM python:3.12-slim
# Set the following enviroment variables
#
# FLASK_APP -> entry point to your flask app
ENV FLASK_APP=app
# FLASK_ENV -> Tell flask to use the production server
ENV FLASK_ENV=production
# SQLALCHEMY_ECHO -> keep off in production (logs every query)
ENV SQLALCHEMY_ECHO=false
# Set the directory for upcoming commands to /var/www
WORKDIR /var/www/
# Copy all the files from your repo to the working directory
COPY . .
# Copy the built react app (it's built for us) from the
# /react-app/build/ directory into your flasks app/static directory
COPY /react-app/build/* app/static/
# Run the next two python install commands with PIP
# install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# (the Postgres driver, psycopg 3, is in requirements.txt)

# Start the flask environment by setting our
# closing command to gunicorn wsgi:app (the app factory entry point)
CMD gunicorn wsgi:app
