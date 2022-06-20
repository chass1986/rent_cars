import werkzeug.exceptions
from flask import request, session, jsonify
from rent_cars import app, db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from rent_cars import login_required
from rent_cars.models import User, License
from rent_cars.utils.formatter import response
from rent_cars.utils.validators import AccountsValidator
from rent_cars.utils.custom_exceptions import (PasswordsNotMatching, WrongFormat,
                                               MissingMandatoryFields, InputNotAcceptable, RecordAlreadyExists)


@app.route('/')
@login_required
def hello_world():  # put application's code here
    passhash = generate_password_hash('chouaib')
    return passhash


@app.route('/login', methods=['POST'])
def login():
    valid_body = AccountsValidator(request)
    try:
        valid_body.login()
    except MissingMandatoryFields as e:
        return response(e.message, e.status_code)

    body = request.json
    try:
        row = User.query.filter_by(username=body['username']).first_or_404()
    except werkzeug.exceptions.NotFound:
        return response('Invalid Credentials', 400)

    if not check_password_hash(row.password, body['password']):
        return response('Invalid Credentials', 400)

    row.last_login = datetime.utcnow()
    db.session.commit()
    session['user'] = jsonify(row).json

    return response('You are logged in successfully.')


@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)

    return response('You are logged out successfully.')


@app.route('/register', methods=['POST'])
def register():
    valid_body = AccountsValidator(request)
    try:
        valid_body.registration()
    except (MissingMandatoryFields, WrongFormat, InputNotAcceptable, PasswordsNotMatching, RecordAlreadyExists) as e:
        return response(e.message, e.status_code)

    body = request.json
    hashed_password = generate_password_hash(body['password1'])
    user = User(username=body['username'], email=body['email'], password=hashed_password)
    db.session.add(user)
    db.session.commit()

    license = License(license_number=body['license_number'], date_issued=body['date_issued'],
                      date_expiry=body['date_expiry'], user_id=user.id)
    db.session.add(license)
    db.session.commit()

    return response("User created successfully", data=user)

