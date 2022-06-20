from werkzeug.security import generate_password_hash

from rent_cars import app, login_required, admin_required, db
from rent_cars.models import User
from flask import request, session

from rent_cars.utils.core import paginate_results
from rent_cars.utils.custom_exceptions import (WrongType, InputNotAcceptable, RecordAlreadyExists,
                                               MissingMandatoryFields, WrongFormat, PasswordsNotMatching)
from rent_cars.utils.formatter import response
from rent_cars.utils.validators import AccountsValidator
from rent_cars.config import ROWS_PER_PAGE


@app.route('/users', methods=['GET', 'POST'])
@admin_required
@login_required
def manage_users():
    """
    admin users can fetch all the users info
    admin can use this endpoint for POST
    """
    if session['user']['is_admin'] and request.method == 'POST':
        user_validator = AccountsValidator(request)
        try:
            mandatory_fields = user_validator.registration()
        except (MissingMandatoryFields, WrongFormat, InputNotAcceptable,
                PasswordsNotMatching, RecordAlreadyExists) as e:
            return response(e.message, e.status_code)
        body = request.json
        params = {field: body.get(field) for field in mandatory_fields}

        user = User(**params)
        db.session.add(user)
        db.session.commit()

        return response('User created successfully')

    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=ROWS_PER_PAGE)
    res = paginate_results(users, request)

    return response("Users fetched successfully", data=res)


@app.route('/users/<user_id>/user', methods=['GET', 'DELETE', 'PATCH'])
@login_required
def mange_user(user_id):
    """
    admin user can fetch any user info
    base user can fetch only his user info
    only admin user delete accounts
    """
    user = User.query.filter_by(id=user_id).first()
    current_user_id = session['user']['id']
    is_admin = session['user']['is_admin']

    if request.method == 'GET':
        # admin can fetch any user
        # base user will fetch only his user info
        if user and is_admin or user and user.id == current_user_id:
            return response('User fetched successfully', data=user)
        else:
            return response('user not found', 404)
    elif request.method == 'PATCH':
        if not user or current_user_id != user.id:
            return response('User not found', 404)

        user_validator = AccountsValidator(request)
        try:
            user_validator.update_user()
        except (WrongType, InputNotAcceptable, RecordAlreadyExists) as e:
            return response(e.message, e.status_code)

        body = request.json
        if body.get('username'):
            user.username = body['username']
        if body.get('password'):
            user.password = generate_password_hash(body['password'])

        if is_admin and body.get('is_admin'):
            user.is_admin = body['is_admin']

        db.session.commit()
        return response(f"user {user.id} updated successfully")
    else:  # DELETE
        if not is_admin:
            return response('Access to this resource is denied', 403)

        db.session.delete(user)
        db.session.commit()

        return response('User deleted successfully')
