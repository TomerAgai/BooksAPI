from flask import Blueprint, request, jsonify
from utils import fetch_from_google_books, fetch_language_from_openlibrary, generate_summary, generate_book_id

book_bp = Blueprint('book_bp', __name__)

# Sample data structure for storing books and ratings
books = {}
ratings = {}
ACCEPTED_GENRES = {'Fiction', 'Children', 'Biography', 'Science', 'Science Fiction', 'Fantasy', 'Other'}

@book_bp.route('/', methods=['POST'])
def create_book():
    # Check for correct content type
    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type, expected application/json'}), 415

    data = request.get_json()
    
    # Check for required fields
    for field in ['title', 'ISBN', 'genre']:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 422

    title = data['title']
    isbn = data['ISBN']
    genre = data['genre']

    if genre not in ACCEPTED_GENRES:
        return jsonify({'error': 'Invalid genre provided'}), 422
    
    if any(book for book in books.values() if book['ISBN'] == isbn):
        return jsonify({'error': 'ISBN already exists'}), 422

    # Fetch data from external APIs
    try:
        authors, publisher, publishedDate = fetch_from_google_books(isbn)
        if not authors or not publisher:
            raise ValueError("Google Books API returned incomplete data.")
        
        languages = fetch_language_from_openlibrary(isbn)
        if not languages:
            raise ValueError("OpenLibrary API returned incomplete data.")
        
        summary = generate_summary(title, authors)
        if not summary:
            raise ValueError("LLM API returned incomplete data.")
    except Exception as e:
        return jsonify({'error': f'unable to connect to external service: {str(e)}'}), 500

    # Create book entry
    book_id = generate_book_id()
    new_book = {
        'id': book_id,
        'title': title,
        'authors': authors,
        'ISBN': isbn,
        'publisher': publisher,
        'publishedDate': publishedDate,
        'genre': genre,
        'language': languages,
        'summary': summary
    }
    books[book_id] = new_book

    ratings[book_id] = {
        'values': [],
        'average': 0.0,
        'title': title,
        'id': book_id
    }

    return jsonify({'id': book_id}), 201

@book_bp.route('/', methods=['GET'])
def get_books():
    query_parameters = request.args
    filtered_books = books.values()

    # Standard field filtering
    standard_fields = ['title', 'authors', 'ISBN', 'publisher', 'publishedDate', 'genre', 'id']
    for field in standard_fields:
        if field in query_parameters:
            value = query_parameters[field]
            filtered_books = [book for book in filtered_books if book.get(field) == value]

    # Language filtering with multiple possible parameter names
    possible_language_keys = ['language_contains', 'language contains', 'language-contain', 'language']
    language_query = next((query_parameters[key] for key in possible_language_keys if key in query_parameters), None)
    
    if language_query:
        filtered_books = [book for book in filtered_books if language_query in book.get('language', [])]

    return jsonify(list(filtered_books)), 200


@book_bp.route('/<string:id>', methods=['GET', 'DELETE'])
def book_resource(id):
    if request.method == 'GET':
        book = books.get(id, None) 
        if book is not None:
            return jsonify(book), 200 
        else:
            return jsonify({'error': 'Book not found'}), 404

    elif request.method == 'DELETE':
        if id in books and id in ratings:
            del books[id]
            del ratings[id]
            return jsonify({'id': id}), 200 
        else:
            return jsonify({'error': 'Book not found'}), 404

@book_bp.route('/<string:id>', methods=['PUT'])
def update_book(id):
    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type, expected application/json'}), 415

    if id not in books:
        return jsonify({'error': 'Book not found'}), 404

    data = request.get_json()
    required_fields = {'title', 'authors', 'ISBN', 'publisher', 'publishedDate', 'genre', 'language', 'summary'}
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing fields, all fields must be provided'}), 422

    if any(key not in required_fields for key in data.keys()):
        return jsonify({'error': 'Invalid fields provided, update rejected'}), 422

    if data['genre'] not in ACCEPTED_GENRES:
        return jsonify({'error': 'Invalid genre provided'}), 422

    books[id].update({
        'title': data['title'],
        'authors': data['authors'],
        'ISBN': data['ISBN'],
        'publisher': data['publisher'],
        'publishedDate': data['publishedDate'],
        'genre': data['genre'],
        'language': data['language'],
        'summary': data['summary']
    })

    return jsonify({'id': id}), 200