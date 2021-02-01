from tqdm import tqdm
import django
import environ
import os
from sys import argv
from django.conf import settings

if len(argv) != 2:
    print('No filename was passed')
    exit()

filename = argv[1]

env = environ.Env()
environ.Env.read_env('autoelect/settings/.env')

#### DJANGO SETUP
settings.configure(
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)),

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DATABASE_PRIMARY'),
            'HOST': env('DATABASE_HOST'),
            'PORT': env('DATABASE_PORT'),
            'USER': env('DATABASE_USER_PRIMARY'),
            'PASSWORD': env('DATABASE_PASSWORD_PRIMARY'),
        }
    },

    EMAIL_HOST = env('EMAIL_HOST'),
    EMAIL_HOST_USER = env('EMAIL_HOST_USER'),
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD'),
    EMAIL_PORT = int(env('EMAIL_PORT')),
    EMAIL_USE_TLS = True,

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'vote',
        'audit_trail',
    ]
)
django.setup()

from vote.models import AuthUser as User

fp = open(filename)
n = 500

for i in tqdm(range(n)):
    line = fp.readline()
    id_number, password = line.split(',')
    
    id_number = id_number.strip()
    password = password.strip()

    user = User.objects.get(username=id_number)
    user.set_password(password)
    user.save()

fp.close()