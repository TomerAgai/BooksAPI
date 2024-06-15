from flask import Blueprint, request, jsonify
from ..utils import get_book_details
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime

loan_bp = Blueprint('loan_bp', __name__)
mongo = PyMongo()

@loan_bp.route('/', methods=['POST'])
def create_loan():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type, expected application/json'}), 415

    data = request.get_json()
    for field in ['memberName', 'ISBN', 'loanDate']:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 422

    member_name = data['memberName']
    isbn = data['ISBN']
    loan_date = data['loanDate']

    # Validate loan date format
    try:
        datetime.strptime(loan_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format, expected YYYY-MM-DD'}), 422

    # Check if the member already has 2 or more books on loan
    member_loans_count = mongo.db.loans.count_documents({'memberName': member_name})
    if member_loans_count >= 2:
        return jsonify({'error': 'Member already has 2 or more books on loan'}), 422
    
    try:
        book_details = get_book_details(isbn)
    except Exception as e:
        return jsonify({'error': str(e)}), 422
    
    book_id = ObjectId(book_details['_id'])
    
    # Check if the book is already on loan
    book_on_loan = mongo.db.loans.find_one({'bookID': book_id})
    if book_on_loan:
        return jsonify({'error': 'Book is already on loan'}), 422

    new_loan = {
        'memberName': member_name,
        'ISBN': isbn,
        'title': book_details['title'],
        'bookID': book_id,
        'loanDate': loan_date
    }
    loan_id = mongo.db.loans.insert_one(new_loan).inserted_id
    return jsonify({'loanID': str(loan_id)}), 201

@loan_bp.route('/', methods=['GET'])
def get_loans():
    query_parameters = request.args
    query = {}

    for field in ['memberName', 'ISBN', 'loanDate', 'title', 'bookID']:
        if field in query_parameters:
            query[field] = query_parameters[field]

    loans = list(mongo.db.loans.find(query))
    for loan in loans:
        loan['_id'] = str(loan['_id'])
        loan['bookID'] = str(loan['bookID'])  

    return jsonify(loans), 200

@loan_bp.route('/<string:loan_id>', methods=['GET'])
def get_loan(loan_id):
    try:
        loan = mongo.db.loans.find_one({'_id': ObjectId(loan_id)})
    except:
        return jsonify({'error': 'Invalid loan ID'}), 400

    if loan:
        loan['_id'] = str(loan['_id'])
        loan['bookID'] = str(loan['bookID']) 
        return jsonify(loan), 200
    else:
        return jsonify({'error': 'Loan not found'}), 404

@loan_bp.route('/<string:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    try:
        object_id = ObjectId(loan_id)
    except:
        return jsonify({'error': 'Invalid loan ID'}), 400

    result = mongo.db.loans.delete_one({'_id': object_id})
    
    if result.deleted_count > 0:
        return jsonify({'loanID': loan_id}), 200
    else:
        return jsonify({'error': 'Loan not found'}), 404