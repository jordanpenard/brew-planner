# brew-planner

## Deployment notes
A secret file needs to be created as `brew-planner/secret.py`, and it's content should
be `SECRET_KEY = '<put secure key here>'`

## Django manager how-to
- Create DB migration script : `python manage.py makemigrations stock`
- Apply DB migration script : `python manage.py migrate`
- Run server : `python manage.py runserver`
