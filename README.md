# Brew Planner

## Deployment
The following needs to be setup while deploying the container :
- Port mapping for `TCP:80`
- Volume mapping for `/data`

Once a container is freshly deployed, there's a few things that needs setting up for the first time
```
cd /var/www/html
rm index.html
git clone https://github.com/jordanpenard/brew-planner.git .
ln -s /data/db.sqlite3 /var/www/html/db.sqlite3
ln -s /data/secret.py /var/www/html/brew-planner/secret.py
echo "SECRET_KEY = '$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')'" > /data/secret.py
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py createsuperuser
chown -R www-data:www-data /data
chown -R www-data:www-data /var/www/html
```

You will also need to change `CSRF_TRUSTED_ORIGINS` inside `brew-planner/settings.py` to match your public url in order to avoid a `CSRF verification failed` error.

## Update
In case of an update to a new version, only the following should be required, and a backup of the database is recommended
```
cd /data
cp db.sqlite3 db.sqlite3.bak
cd /var/www/html
git pull
python3 manage.py migrate
chown -R www-data:www-data /data
chown -R www-data:www-data /var/www/html
```
