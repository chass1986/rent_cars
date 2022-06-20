from werkzeug.security import generate_password_hash

from rent_cars import app, login_required, admin_required, db
from rent_cars.models import Car
from flask import request, session

from rent_cars.utils.core import paginate_results
from rent_cars.utils.custom_exceptions import (WrongType, InputNotAcceptable, RecordAlreadyExists,
                                               MissingMandatoryFields, WrongFormat, PasswordsNotMatching)
from rent_cars.utils.formatter import response
from rent_cars.utils.validators import CarsValidator
from rent_cars.config import ROWS_PER_PAGE


@app.route('/cars', methods=['GET', 'POST'])
@login_required
def manage_cars():
    """
    Base user will get only the cars that are available (is_available=True)
    Admin user will get all the cars (available and unavailable)
    only admin can add new car
    """
    if session['user']['is_admin'] and request.method == 'POST':
        car_validator = CarsValidator(request)
        try:
            mandatory_fields = car_validator.add_car()
        except (MissingMandatoryFields, WrongFormat, InputNotAcceptable,
                PasswordsNotMatching, RecordAlreadyExists) as e:
            return response(e.message, e.status_code)
        body = request.json
        params = {field: body.get(field) for field in mandatory_fields}

        car = Car(**params)
        db.session.add(car)
        db.session.commit()

        return response('Car created successfully', data=car)

    page = request.args.get('page', 1, type=int)
    if session['user']['is_admin']:
        cars = Car.query.paginate(page=page, per_page=ROWS_PER_PAGE)
    else:
        cars = Car.query.filter_by(is_available=True).paginate(page=page, per_page=ROWS_PER_PAGE)
    res = paginate_results(cars, request)

    return response("Cars fetched successfully", data=res)


@app.route('/cars/<car_id>/car', methods=['GET', 'DELETE', 'PATCH'])
@login_required
def get_car(car_id):
    car = Car.query.filter_by(id=car_id).first()
    is_admin = session['user']['is_admin']

    if request.method == 'GET':
        if car:
            return response('Car fetched successfully', data=car)
        else:
            return response('Car not found', 404)
    elif request.method == 'PATCH' and is_admin:
        if not car:
            return response('Car not found', 404)

        car_validator = CarsValidator(request)
        try:
            allowed_fields = car_validator.update_car()
        except (WrongType, InputNotAcceptable, RecordAlreadyExists) as e:
            return response(e.message, e.status_code)

        body = request.json
        for field_name, field_value in body.items():
            if field_name in allowed_fields:
                car.field_name = field_value

        if is_admin and 'is_available' in body:
            car.is_admin = body['is_available']
        db.session.commit()
        return response(f"Car {car.id} updated successfully")
    else:  # DELETE
        if not is_admin:
            return response('Access to this resource is denied', 403)

        db.session.delete(car)
        db.session.commit()

        return response('Car deleted successfully')
