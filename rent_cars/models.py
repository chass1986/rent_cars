from datetime import datetime
from dataclasses import dataclass, field
from sqlalchemy.orm import backref
import enum

from rent_cars import db


@dataclass
class License(db.Model):
    license_number: str = db.Column(db.String(15), unique=True, nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    date_issued: datetime = db.Column(db.TIMESTAMP, nullable=False)
    date_expiry: datetime = db.Column(db.TIMESTAMP, nullable=False)
    id: int = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"License({self.number})"


@dataclass
class Reservation(db.Model):
    class ReservationStatus(enum.Enum):
        reserved = 'reserved'
        cancelled = 'cancelled'

    id: int = db.Column(db.Integer, primary_key=True)
    car_id: int = db.Column(db.Integer, db.ForeignKey('car.id'), unique=True, nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    status = db.Column(db.Enum(ReservationStatus), default=ReservationStatus.reserved, nullable=False)
    reservation_start_date: datetime = db.Column(db.TIMESTAMP, nullable=False)
    reservation_end_date: datetime = db.Column(db.TIMESTAMP, nullable=False)
    date_last_update: datetime = db.Column(db.TIMESTAMP, nullable=True)
    date_created: datetime = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Location({self.latitude}, {self.longitude})"


@dataclass
class User(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    licenses: License = db.relationship('License', backref='user', uselist=False, cascade='all,delete')
    reservation: Reservation = db.relationship('Reservation', backref='user', uselist=False, cascade='all,delete')
    username: str = db.Column(db.String(25), unique=True, nullable=False)
    email: str = db.Column(db.String(150), unique=True, nullable=False)
    last_login: datetime = db.Column(db.TIMESTAMP, nullable=True)
    date_created: datetime = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    is_admin: bool = db.Column(db.Boolean, default=False)

    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"User({self.username}, {self.email})"


@dataclass
class Location(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    car_id: int = db.Column(db.Integer, db.ForeignKey('car.id'), unique=True, nullable=False)
    latitude: float = db.Column(db.Float, nullable=False)
    longitude: float = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Location({self.latitude}, {self.longitude})"


@dataclass
class Car(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    current_location: Location = db.relationship('Location', backref='car', uselist=False, cascade='all,delete')
    reservation: Reservation = db.relationship('Reservation', backref='car', uselist=False, cascade='all,delete')
    license_plate: str = db.Column(db.String(15), unique=True, nullable=False)
    company: str = db.Column(db.String(15), nullable=False)
    model: str = db.Column(db.String(20), nullable=False)
    fabrication_year: str = db.Column(db.String(4), nullable=False)
    number_of_seats: int = db.Column(db.Integer, nullable=False)
    is_available: bool = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"Car({self.license_plate}, {self.model}, {self.is_available})"
