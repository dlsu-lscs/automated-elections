# NOTE: Create data databases first
# found in migrations/init.sql

# Migrate main database
python3 manage.py migrate

# Create super user admin
python3 manage.py createsuperuser

# Create database for vote1, vote2, vote3
cd migrations
sh up.sh

# Insert data into primary
sh insert.sh

# Go back to main folder
cd ..
