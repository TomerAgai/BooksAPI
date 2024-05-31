from flask import Blueprint, request, jsonify
from ..utils import fetch_from_google_books, generate_book_id
from flask_pymongo import PyMongo

book_bp = Blueprint('book_bp', __name__)
mongo = PyMongo()

ACCEPTED_GENRES = {'Fiction', 'Children', 'Biography', 'Science', 'Science Fiction', 'Fantasy', 'Other'}

@book_bp.route('/', methods=['POST'])
def create_book():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type, expected application/json'}), 415

    data = request.get_json()
    for field in ['title', 'ISBN', 'genre']:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 422

    title = data['title']
    isbn = data['ISBN']
    genre = data['genre']

    if genre not in ACCEPTED_GENRES:
        return jsonify({'error': 'Invalid genre provided'}), 422

    existing_book = mongo.db.books.find_one({'ISBN': isbn})
    if existing_book:
        return jsonify({'error': 'ISBN already exists'}), 422

    try:
        authors, publisher, publishedDate = fetch_from_google_books(isbn)
        if not authors or not publisher:
            raise ValueError("Google Books API returned incomplete data.")
    except Exception as e:
        return jsonify({'error': f'unable to connect to external service: {str(e)}'}), 500

    book_id = generate_book_id()
    new_book = {
        '_id': book_id,
        'title': title,
        'authors': authors,
        'ISBN': isbn,
        'publisher': publisher,
        'publishedDate': publishedDate,
        'genre': genre
    }
    mongo.db.books.insert_one(new_book)

    new_rating = {
        '_id': book_id,
        'values': [],
        'average': 0.0,
        'title': title
    }
    mongo.db.ratings.insert_one(new_rating)

    return jsonify({'id': book_id}), 201

@book_bp.route('/', methods=['GET'])
def get_books():
    query_parameters = request.args
    query = {}

    for field in ['title', 'authors', 'ISBN', 'publisher', 'publishedDate', 'genre', '_id']:
        if field in query_parameters:
            query[field] = query_parameters[field]

    books = list(mongo.db.books.find(query))
    for book in books:
        book['_id'] = str(book['_id'])

    return jsonify(books), 200

@book_bp.route('/<string:id>', methods=['GET', 'DELETE'])
def book_resource(id):
    if request.method == 'GET':
        book = mongo.db.books.find_one({'_id': id})
        if book:
            book['_id'] = str(book['_id'])
            return jsonify(book), 200
        else:
            return jsonify({'error': 'Book not found'}), 404

    elif request.method == 'DELETE':
        book_result = mongo.db.books.delete_one({'_id': id})
        rating_result = mongo.db.ratings.delete_one({'_id': id})
        if book_result.deleted_count > 0 and rating_result.deleted_count > 0:
            return jsonify({'id': id}), 200
        else:
            return jsonify({'error': 'Book not found'}), 404

@book_bp.route('/<string:id>', methods=['PUT'])
def update_book(id):
    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type, expected application/json'}), 415

    data = request.get_json()
    required_fields = {'title', 'authors', 'ISBN', 'publisher', 'publishedDate', 'genre'}
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing fields, all fields must be provided'}), 422

    if any(key not in required_fields for key in data.keys()):
        return jsonify({'error': 'Invalid fields provided, update rejected'}), 422

    if data['genre'] not in ACCEPTED_GENRES:
        return jsonify({'error': 'Invalid genre provided'}), 422

    update_result = mongo.db.books.update_one({'_id': id}, {'$set': data})
    if update_result.matched_count > 0:
        return jsonify({'id': id}), 200
    else:
        return jsonify({'error': 'Book not found'}), 404
