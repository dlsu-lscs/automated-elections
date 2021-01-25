# Requirements
python, pip, and
virtualenv(pip install)

# SETUP
Read setup.sh and run the following commands there

To run python in virtual env follow these steps

```
# Setup virtual env folder
mkdir virt
virtualenv virt

# Enter virtual env
source virt/bin/activate

# Install the packages in the vitual environment
pip3 install -r requirements

# To exit env
deactivate
```

# Run locally
```
python3 manage.py runserver [-b=<host>:<port>]
```

# Run in production
```
# Set DEBUG = False
gunicorn -c conf/gunicorn_config.py autoelect.wsgi:app
```

# Troubleshooting
- .env is not set so try making one

- Missing css in admin
```
python3 manage.py collectstatic --noinput
```
