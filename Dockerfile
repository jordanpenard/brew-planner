FROM python:3.9

WORKDIR /var/www/html

# Copy the files we need
COPY . /var/www/html/

# Create sym links for the data we want to persiste
RUN ln -s /data/db.sqlite3 /var/www/html/db.sqlite3
RUN ln -s /data/secret.py /var/www/html/brew-planner/secret.py

# Fix permissions
RUN chown -R www-data:www-data /var/www/html

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install stuff
RUN apt-get update
RUN apt-get install -y apache2 apache2-utils git
RUN apt-get install -y libapache2-mod-wsgi-py3
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# port where the Django app runs
EXPOSE 80

# Apache setup
COPY ./site-config.conf /etc/apache2/sites-available/000-default.conf

# start server
CMD ["apache2ctl", "-DFOREGROUND"]
