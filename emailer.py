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

if len(argv) < 2:
    print('No Colleges were passed as arguments')
    exit()

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

##### INPUT VALIDATION
# Get all voters
colleges = argv[1:]

for college in colleges:
    # This will throw an error if object not found
    try:
        College.objects.get(name=college)
    except:
        print('College '' + college + '' was not found')
        exit()

# Get all voters
voters = User.objects.filter(voter__college__name__in=colleges ,voter__voting_status=False, voter__eligibility_status=True)

if voters.count() == 0:
    print('No voters found')
    exit()

######### CONTENT CREATION
# HTML
fp = open(settings.BASE_DIR + '/email_template.html', 'r')
HTML_STR = fp.read()
fp.close()

# IMAGE
fp = open(settings.BASE_DIR + '/ComelecLogo.png', 'rb')
img = base64.b64encode(fp.read()).decode('ascii')
fp.close()

fp = open(settings.BASE_DIR + '/deletethis.csv', 'w')
n = 500

for i in tqdm(range(len(voters))):
    if i % n == 0:
        fp.close()
        fp = open(settings.BASE_DIR + '/accounts_' + str(i // n) + '.csv', 'w')

    voter = voters[i]

    new_password = generate_passcode()

    # save the new password to the database
    voter.set_password(new_password)
    voter.save()

    fp.write(voter.username + ',' + new_password + '\n')

    # TODO: Change URL
    text = '''\
DLSU Comelec is inviting to you to vote in the elections.
Voter ID: {}
Voter Key: {}
To vote, go to this link: https://usg-election.dlsu.edu.ph/login
    '''.format(voter.username, new_password)

    # TODO: make lodash
    html = HTML_STR
    html = html.replace('11xxxxxx', voter, 2)
    html = html.replace('xxxxxxxx', new_password, 1)

    data = {
        'Messages': [
            {
            'From': {
                'Email': 'comelec@usg-election.com',
                'Name': 'DLSU COMELEC'
            },
            'To': [
                { 'Email': voter.email }
            ],
            'Subject': '[COMELEC] Election is now starting',
            'TextPart': text,
            'HTMLPart': html,
            'InlinedAttachments': [
				{
                    'ContentType': 'img/png',
                    'Filename': 'logo.png',
                    'ContentID': 'logo',
                    'Base64Content': img
				}
		    ]
            }
        ]
    }
    result = mailjet.send.create(data=data)
    if result.status_code != 200:
        print('Email did not sent for {}', )

s.close()
fp.close()