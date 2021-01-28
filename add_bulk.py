"""
Adds a bulk of voter in the database
Inserted users format
    username: id_number
    password: randomly generated
    first_name: id_number
    last_name: campus + ' ' +  college

Arguments:
    1: filename/filepath
    2: campus   eg. MNL, LAG
    3: college  eg. CCS, COS

example:
    python add_bulk.py MNL CCS
    python add_bulk.py LAG GCOE
"""

import environ
import os
from random import randint
from tqdm import tqdm
from sys import argv

import django
from django.conf import settings

# ARGUMENTS
if len(argv) != 4:
    print('3 arguments are expected (filename, campus, college)')
    exit()

filename = argv[1]
campus_name = argv[2]
college_name = argv[3]

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

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'vote',
        'audit_trail',
    ]
)
django.setup()

from django.contrib.auth.models import Group
from django.db import IntegrityError
from vote.models import AuthUser as User, Voter, College, Campus

voter_group = Group.objects.get(name='voter')

def generate_passcode():
    length = 8
    charset = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789'
    passcode = ''

    for index in range(length):
        passcode += charset[randint(0, len(charset) - 1)]
    return passcode

fp = open(filename)
# 1st line
# Num of students, College, Campus
line = fp.readline().strip()
size = line

print('Length: {}\nCampus: {}\nCollege: {}'.format(size, campus_name, college_name))
# User input

size = int(size)
campus = None
college = None

try:
    campus = Campus.objects.get(name=campus_name)
except:
    print('Campus not found')
    fp.close()
    exit()

try:
    college = College.objects.get(name=college_name)
except:
    print('College not found')
    fp.close()
    exit()

# 2nd onwards, id numbers
for i in tqdm(range(size)):
    line = fp.readline().strip()

    id_number = line
    batch = line[:3]
    email = id_number + '@dlsu.edu.ph'
    first_name = id_number
    last_name = campus_name + ' ' + college_name
    password = generate_passcode()
    voting_status = False
    eligibility_status = True

    try:
        user = User.objects.create_user(
            username=id_number,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        voter_group.user_set.add(user)

        user.save()

        Voter.objects.create(
            user=user,
            campus=campus,
            college=college,
            batch=batch,
            voting_status=voting_status,
            eligibility_status=eligibility_status
        )
    except IntegrityError:
        print('ID {} is already in the database'.format(id_number))
    except Exception as e:
        print(e)
        print('ID {} was not added'.format(id_number))

fp.close()