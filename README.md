# Brew Planner

## Deployment
The following needs to be setup while deploying the container :
- Port mapping for `TCP:80`

```
docker build .
docker run -dit --name brew-planner --mount type=bind,source=`pwd`,target=/var/www/html -p 8000:80 --restart=always brew-planner
```

Once a container is freshly deployed, there's a few things that needs setting up for the first time
```
cd /var/www/html
echo "SECRET_KEY = '$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')'" > brew-planner/secret.py
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py createsuperuser
chown -R www-data:www-data /var/www/html
```

You will also need to change `CSRF_TRUSTED_ORIGINS` inside `brew-planner/settings.py` to match your public url in order to avoid a `CSRF verification failed` error.

## Updates
When you want to update to a new version, only the following should be required, and a backup of the database is recommended
```
cd /var/www/html
cp db.sqlite3 db.sqlite3.bak
sudo -u www-data git pull
sudo -u www-data python3 manage.py migrate
```
Then restart your container.
