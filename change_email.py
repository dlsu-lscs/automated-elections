'''
Emails a specific college of the system

Arguments
    1-n: colleges eg CCS, COS

ex.
    python emailer.py CCS COS SOE
    python emailer.py CCS
'''

import base64
import smtplib
import environ
import os
from random import randint
from tqdm import tqdm
from sys import argv
from mailjet_rest import Client

import django
from django.conf import settings

if len(argv) != 2:
    print('Filename required')
    exit()

filename = argv[1]

env = environ.Env()
environ.Env.read_env('autoelect/settings/.env')

mailjet = Client(auth=(env('MJ_APIKEY_PUBLIC'), env('MJ_APIKEY_PRIVATE')), version='v3.1')

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

from vote.models import AuthUser as User, Voter, College

def generate_passcode():
    length = 8
    charset = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789'
    passcode = ''

    for index in range(length):
        passcode += charset[randint(0, len(charset) - 1)]
    return passcode

######### CONTENT CREATION
# HTML
fp = open(settings.BASE_DIR + '/email_template.html', 'r')
HTML_STR = fp.read()
fp.close()

# IMAGE
fp = open(settings.BASE_DIR + '/ComelecLogo.png', 'rb')
img = base64.b64encode(fp.read()).decode('ascii')
fp.close()

fp2 = open(filename)
n = 9

for i in tqdm(range(n)):
    line = fp2.readline()
    id_number, email = line.split(',')
    id_number = id_number.strip()
    email = email.strip()

    try:
        voter = User.objects.get(username=id_number)
        voter.email = email
        voter.save()
        
    except Exception as e:
        print(e)
        print('ID not found {}'.format(id_number))

fp.close()
fp2.close()