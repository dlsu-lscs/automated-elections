import environ
import os
from random import randint
from tqdm import tqdm

import django
from django.conf import settings

env = environ.Env()
environ.Env.read_env('autoelect/settings/.env')

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

from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from vote.models import AuthUser as User, Voter

# get all voters
voters = User.objects.filter(voter__voting_status=False, voter__eligibility_status=True)

def generate_passcode():
    length = 8
    charset = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789'
    passcode = ''

    for index in range(length):
        passcode += charset[randint(0, len(charset) - 1)]
    return passcode

# EMAIL BODY CONST
fp = open(settings.BASE_DIR + '/email_template.html', 'r')
HTML_STR = fp.read()
fp.close()


size = len(voters)
i = 0

for voter in voters:
    new_password = generate_passcode()

    # save the new password to the database
    voter.set_password(new_password)
    voter.save()

    fp = open(settings.BASE_DIR + '/ComelecLogo.png', 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    img.add_header('Content-ID', '<logo>')

    # TODO: Change URL
    subject = '[COMELEC] Election is now starting'
    text = '''\
DLSU Comelec is inviting to you to vote in the elections.
Voter ID: {}
Voter Key: {}
To vote, go to this link: https://127.0.0.1:8000/login
    '''.format(voter.username, new_password)

    # TODO: make lodash
    html = HTML_STR
    html = html.replace('11xxxxxx', voter.username, 2)
    html = html.replace('xxxxxxxx', new_password, 1)

    msg = EmailMultiAlternatives(
        subject = subject,
        body = text,
        from_email = 'usg.election@gmail.com',
        to = [ voter.email ]
    )
    msg.attach_alternative(html, "text/html")
    msg.attach(img)
    
    try:
        msg.send()
    except:
        print('Email did not sent for ' + voter.username)
    
    i += 1