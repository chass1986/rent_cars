from flask import jsonify


def paginate_results(pagination, request):
    return {
        'count': pagination.total,
        'next': f"{request.url}?page={pagination.next_num}" if pagination.next_num else None,
        'previous': f"{request.url}?page={pagination.prev_num}" if pagination.prev_num else None,
        'results': [jsonify(row).json for row in pagination.items],
    }
