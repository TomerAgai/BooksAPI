from flask import Blueprint, jsonify, request
from flask_pymongo import PyMongo

rating_bp = Blueprint('rating_bp', __name__)
mongo = PyMongo()

@rating_bp.route('/', methods=['GET'])
def get_ratings():
    book_id = request.args.get('id', default=None)
    if book_id:
        rating = mongo.db.ratings.find_one({'_id': book_id})
        if rating:
            rating['_id'] = str(rating['_id'])
            return jsonify([rating]), 200 
        else:
            return jsonify({'error': 'Rating not found for the given ID'}), 404
    else:
        all_ratings = list(mongo.db.ratings.find())
        for rating in all_ratings:
            rating['_id'] = str(rating['_id'])
        return jsonify(all_ratings), 200

@rating_bp.route('/<string:id>', methods=['GET'])
def get_rating(id):
    rating = mongo.db.ratings.find_one({'_id': id})
    if rating:
        rating['_id'] = str(rating['_id'])
        return jsonify(rating), 200
    else:
        return jsonify({'error': 'Rating not found'}), 404

@rating_bp.route('/<string:id>/values', methods=['POST'])
def add_rating(id):
    rating = mongo.db.ratings.find_one({'_id': id})
    if not rating:
        return jsonify({'error': 'Rating not found'}), 404

    data = request.get_json()
    try:
        new_value = data['value']
        if new_value not in {1, 2, 3, 4, 5}:
            return jsonify({'error': 'Invalid rating value'}), 422
    except (KeyError, TypeError):
        return jsonify({'error': 'Invalid data provided'}), 400

    ratings_values = rating['values']
    ratings_values.append(new_value)
    new_average = round(sum(ratings_values) / len(ratings_values), 2)

    mongo.db.ratings.update_one(
        {'_id': id},
        {'$set': {'values': ratings_values, 'average': new_average}}
    )

    return jsonify({'new_average': new_average}), 200