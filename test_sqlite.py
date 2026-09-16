import os
import django
from django.conf import settings
import uuid

settings.configure(
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'users',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    AUTH_USER_MODEL='users.CustomUser',
)

django.setup()
from django.core.management import call_command
call_command('migrate', verbosity=0)

from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.create_user(username='test', password='old')
print('Before reset password check:', user.check_password('old'))

user = User.objects.get(username='test')
user.set_password('new')
user.save()

user = User.objects.get(username='test')
print('After reset password check new:', user.check_password('new'))
print('After reset password check old:', user.check_password('old'))
