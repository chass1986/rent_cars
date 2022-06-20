from flask import session, jsonify
from .formatter import response


def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return response('Unauthorized', 401)
        return f(*args, **kwargs)
    #  to fix: View function mapping is overwriting an existing endpoint function: decorator_function
    wrapper.__name__ = f.__name__

    return wrapper


def admin_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('user', {}).get('is_admin'):
            return response('Access to this resource is denied', 403)
        return f(*args, **kwargs)
    #  to fix: View function mapping is overwriting an existing endpoint function: decorator_function
    wrapper.__name__ = f.__name__

    return wrapper
