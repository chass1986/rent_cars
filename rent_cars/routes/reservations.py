from werkzeug.security import generate_password_hash

from rent_cars import app, login_required, admin_required, db
from rent_cars.models import User, Reservation, Car
from flask import request, session

from rent_cars.utils.core import paginate_results
from rent_cars.utils.custom_exceptions import (WrongType, InputNotAcceptable, RecordAlreadyExists,
                                               MissingMandatoryFields, WrongFormat, PasswordsNotMatching)
from rent_cars.utils.formatter import response
from rent_cars.utils.validators import AccountsValidator, ReservationsValidator
from rent_cars.config import ROWS_PER_PAGE


@app.route('/reservations', methods=['GET', 'POST'])
@login_required
def manage_reservations():
    """
    admin user can list all reservations
    base user can add new reservation
    """
    if request.method == 'POST':
        reservation_validator = ReservationsValidator(request)
        try:
            mandatory_fields = reservation_validator.add_reservation()
        except (MissingMandatoryFields, WrongFormat, InputNotAcceptable,
                PasswordsNotMatching, RecordAlreadyExists) as e:
            return response(e.message, e.status_code)
        body = request.json
        car_id = body.get('car_id')
        params = {field: body.get(field) for field in mandatory_fields}
        current_user_id = session['user']['id']
        params['user_id'] = current_user_id

        reservation = Reservation(**params)
        db.session.add(reservation)

        # car not available anymore
        car = Car.query.filter_by(id=car_id).first()
        car.is_available = False

        db.session.commit()
        return response('Reservation created successfully', data=reservation)

    else:
        page = request.args.get('page', 1, type=int)
        if session['user']['is_admin']:
            reservations = Reservation.query.paginate(page=page, per_page=ROWS_PER_PAGE)
        else:
            # get reservations of current user only
            current_user_id = session['user']['id']
            reservations = Reservation.query.filter_by(user_id=current_user_id).paginate(page=page, per_page=ROWS_PER_PAGE)

        res = paginate_results(reservations, request)
        return response("Reservations fetched successfully", data=res)


@app.route('/reservations/<reservation_id>/reservation', methods=['GET'])
@login_required
def get_reservation(reservation_id):
    reservation = Reservation.query.filter_by(id=reservation_id).first()
    current_user_id = session['user']['id']

    if not reservation or reservation.id != current_user_id:
        return response('Reservation not found', 404)

    return response('Reservation fetched successfully', data=reservation)


@app.route('/reservations/<reservation_id>/cancel', methods=['PATCH'])
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.filter_by(id=reservation_id).first()
    if not reservation:
        return response('Reservation not found', 404)

    #
    car = Car.query.filter_by(id=reservation.car_id).first()
    reservation.status = 'cancelled'
    car.is_available = True

    db.session.commit()

    return response('Reservation cancelled successfully')


@app.route('/reservations/<reservation_id>/reservation', methods=['DELETE'])
@admin_required
@login_required
def delete_reservation(reservation_id):
    reservation = Reservation.query.filter_by(id=reservation_id).first()

    if not reservation:
        return response('Reservation not found', 404)

    db.session.delete(reservation)
    db.session.commit()

    return response('Reservation deleted successfully')
