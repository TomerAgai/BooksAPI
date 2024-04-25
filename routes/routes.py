from flask import Blueprint, jsonify
from .book_routes import book_bp
from .rating_routes import rating_bp
from .book_routes import ratings

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(book_bp, url_prefix='/books')
api_bp.register_blueprint(rating_bp, url_prefix='/ratings')

@api_bp.route('/top', methods=['GET'])
def get_top_rated_books():
    eligible_books = [rating for rating in ratings.values() if len(rating['values']) >= 3]
    if not eligible_books:
        return jsonify([]), 200
    
    sorted_books = sorted(eligible_books, key=lambda x: x['average'], reverse=True)

    # Find the top 3 scores (there may be more than 3 books if scores are tied)
    top_scores = sorted(set(book['average'] for book in sorted_books), reverse=True)[:3]

    # Collect all books that have a top 3 score
    top_books = [book for book in sorted_books if book['average'] in top_scores]
    result = [{
        'id': book['id'],
        'title': book['title'],
        'average': book['average']
    } for book in top_books]

    return jsonify(result), 200