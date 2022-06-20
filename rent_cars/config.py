"""
This file won't be pushed to git, it should be copied directly to server
or user env-variables
"""

import os

ROWS_PER_PAGE = 2
SECRET_KEY = os.environ['SECRET_KEY']
SESSION_LIFETIME = 60

user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
database = os.environ['POSTGRES_DB']
host = os.environ.get('POSTGRES_HOST', 'localhost')

DATABASE_URI = f'postgresql://{user}:{password}@{host}/{database}'
