from flask import Blueprint, jsonify
from flask_pymongo import PyMongo

top_bp = Blueprint('top_bp', __name__)
mongo = PyMongo()

@top_bp.route('/', methods=['GET'])
def get_top_rated_books():
    ratings = list(mongo.db.ratings.find())
    
    # Filter eligible books
    eligible_books = [rating for rating in ratings if len(rating['values']) >= 3]
    if not eligible_books:
        return jsonify([]), 200

    # Sort books by average rating in descending order
    sorted_books = sorted(eligible_books, key=lambda x: x['average'], reverse=True)

    # Find the top 3 scores (there may be more than 3 books if scores are tied)
    top_scores = sorted(set(book['average'] for book in sorted_books), reverse=True)[:3]

    # Collect all books that have a top 3 score
    top_books = [book for book in sorted_books if book['average'] in top_scores]
    result = [{
        'id': str(book['_id']), 
        'title': book['title'],
        'average': book['average']
    } for book in top_books]

    return jsonify(result), 200