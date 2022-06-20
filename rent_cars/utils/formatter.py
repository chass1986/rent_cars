from flask import jsonify


def response(message, status_code=200, data=None):
    res = jsonify(
        {
            'message': message,
            'data': data
        }
    )
    res.status_code = status_code

    return res
