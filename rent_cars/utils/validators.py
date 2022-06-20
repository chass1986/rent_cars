import werkzeug.exceptions
from flask import session

from .custom_exceptions import MissingMandatoryFields, PasswordsNotMatching, WrongFormat, InputNotAcceptable, \
    RecordAlreadyExists, WrongType, RecordNotFound
from datetime import datetime
from rent_cars.models import User, License, Car


class BaseValidator:
    mandatory_fields = []
    optional_fields = {}

    def __init__(self, request):
        try:
            self.body = request.json
        except werkzeug.exceptions.BadRequest:
            self.body = {}

    @staticmethod
    def _validate_field_uniqueness(model, field_name, field_value):
        if model.query.filter_by(**{field_name: field_value}).first():
            raise RecordAlreadyExists(
                f"{field_name} already exists"
            )

    def _validate_fields(self):
        missing_fields = [field for field in self.mandatory_fields if field not in self.body]
        if missing_fields:
            raise MissingMandatoryFields(
                f'Mandatory field(s) Missing: {missing_fields}'
            )

    def _validate_fields_content_type(self):
        wrong_types = [
            f"{field_name} should be of type {field_data['type']}"
            for field_name, field_data in self.optional_fields.items()
            if not isinstance(field_data['value'], field_data['type'])
        ]

        if wrong_types:
            raise WrongType(f'The type of values of some fields is wrong. {wrong_types}')

    @staticmethod
    def _validate_datetime_field(field_value, field_format='%Y-%m-%d'):
        try:
            datetime_obj = datetime.strptime(field_value, field_format)
        except ValueError:
            raise WrongFormat(f"Format of datetime is wrong. Accepted format: {field_format}")

        return datetime_obj


class AccountsValidator(BaseValidator):
    def registration(self):
        self.mandatory_fields = ['username', 'email', 'password1', 'password2', 'license_number',
                                 'date_issued', 'date_expiry']
        self._validate_fields()
        self._validate_field_uniqueness(User, 'email', self.body['email'])
        self._validate_license_info()

        return self.mandatory_fields

    def login(self):
        self.mandatory_fields = ['username', 'password']
        self._validate_fields()

    def update_user(self):
        is_admin = session['user']['is_admin']
        self.optional_fields = {
            'username': {'type': str, 'value': self.body.get('username')},
            'password': {'type': str, 'value': self.body.get('password')}
        }
        if is_admin:
            self.optional_fields['is_admin'] = {'type': bool, 'value': self.body.get('is_admin')}

        self._validate_fields_content_type()

        self._validate_field_uniqueness(User, 'username', self.optional_fields['username']['value'])

        return self.optional_fields

    def _validate_license_info(self):
        # license number is alphanumeric of length (12 or 9)
        license_number = self.body['license_number']
        if len(license_number) not in [12, 9] or not license_number.isalnum():
            raise WrongFormat('License number is not valid')

        # license dates are of format YYYY-MM-DD
        _ = self._validate_datetime_field(self.body['date_issued'])
        d_expiry = self._validate_datetime_field(self.body['date_expiry'])

        # license that expires in less than 90 days won't be accepted
        today = datetime.today()
        if (d_expiry - today).days < 90:
            raise InputNotAcceptable(
                "License will expire in less than 90 days"
            )

        # validate uniqueness of license_number
        self._validate_field_uniqueness(License, field_name='license_number', field_value=self.body['license_number'])

    def _validate_password(self):
        if self.body['password1'] != self.body['password2']:
            raise PasswordsNotMatching("Passwords don't matching")


class CarsValidator(BaseValidator):
    def add_car(self):
        body = self.body
        self.mandatory_fields = ['license_plate', 'company', 'model', 'fabrication_year', 'number_of_seats']
        self._validate_fields()
        self._validate_field_uniqueness(Car, 'license_plate', body['license_plate'])

        return self.mandatory_fields

    def update_car(self):
        self.optional_fields = {
            'license_plate': {'type': str, 'value': self.body.get('license_plate')},
            'company': {'type': str, 'value': self.body.get('company')},
            'model': {'type': str, 'value': self.body.get('model')},
            'fabrication_year': {'type': str, 'value': self.body.get('fabrication_year')},
            'number_of_seats': {'type': int, 'value': self.body.get('number_of_seats')},
        }

        if session['user']['is_admin']:
            self.optional_fields['is_available'] = {'type': bool, 'value': self.body.get('is_available')}

        self._validate_fields_content_type()


class ReservationsValidator(BaseValidator):
    def add_reservation(self):
        self.mandatory_fields = ['car_id', 'reservation_start_date', 'reservation_end_date']
        self._validate_fields()
        self._validate_car_existence()
        self._validate_datetime_field(self.body['reservation_start_date'], '%Y-%m-%d %H:%M')
        self._validate_datetime_field(self.body['reservation_end_date'], '%Y-%m-%d %H:%M')

        return self.mandatory_fields

    def _validate_car_existence(self):
        car_id = self.body.get('car_id')
        car = Car.query.filter_by(id=car_id).first()
        if not car:
            raise RecordNotFound(f'Car {car_id} not found')
