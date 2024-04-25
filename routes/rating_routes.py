from flask import Blueprint, jsonify, request
from .book_routes import ratings

rating_bp = Blueprint('rating_bp', __name__)

@rating_bp.route('/', methods=['GET'])
def get_ratings():
    book_id = request.args.get('id', default=None)
    if book_id:
        rating = ratings.get(book_id, None)
        if rating is not None:
            return jsonify([rating]), 200 
        else:
            return jsonify({'error': 'Rating not found for the given ID'}), 404
    else:
        all_ratings = list(ratings.values())
        return jsonify(all_ratings), 200


@rating_bp.route('/<string:id>', methods=['GET'])
def get_rating(id):
    rating = ratings.get(id, None)
    if rating is not None:
        return jsonify(rating), 200
    else:
        return jsonify({'error': 'Rating not found'}), 404

@rating_bp.route('/<string:id>/values', methods=['POST'])
def add_rating(id):
    if id not in ratings:
        return jsonify({'error': 'Rating not found'}), 404

    data = request.get_json()
    try:
        new_value = data['value']
        if new_value not in {1, 2, 3, 4, 5}:
            return jsonify({'error': 'Invalid rating value'}), 422
    except (KeyError, TypeError):
        return jsonify({'error': 'Invalid data provided'}), 400

    ratings[id]['values'].append(new_value)
    ratings[id]['average'] = round(sum(ratings[id]['values']) / len(ratings[id]['values']), 2)
    
    return jsonify({'new_average': ratings[id]['average']}), 200