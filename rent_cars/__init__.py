from datetime import timedelta

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

from rent_cars.utils.accounts import login_required, admin_required
from rent_cars.config import SECRET_KEY, DATABASE_URI, SESSION_LIFETIME

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=SESSION_LIFETIME)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.app_context().push()
CORS(app)
db = SQLAlchemy(app)
db.init_app(app)
db.create_all()

from rent_cars.routes import accounts, users, cars, reservations
