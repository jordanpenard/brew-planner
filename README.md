# brew-planner

## Deployment notes
The following needs to be setup while deploying the container :
- Port mapping for `TCP:80`
- Volume mapping for `/data`

Once a container is freshly deployed, there's a few things that needs setting up for the first time
```
cd /var/www/html
echo "SECRET_KEY = '$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')'" > /data/secret.py
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py createsuperuser
chown -R www-data:www-data /data
chown -R www-data:www-data /var/www/html
```

You will also need to change `CSRF_TRUSTED_ORIGINS` inside `brew-planner/settings.py` to match your public url in order to avoid a `CSRF verification failed` error.

In case of deployment of a new version (new image), only the following should be required
```
cd /var/www/html
python3 manage.py migrate
python3 manage.py collectstatic
chown -R www-data:www-data /data
chown -R www-data:www-data /var/www/html
```
