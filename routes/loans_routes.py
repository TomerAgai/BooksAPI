from flask import Blueprint, request, jsonify
import uuid
from utils import get_book_details
from flask_pymongo import PyMongo

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

    try:
        book_details = get_book_details(isbn)
    except Exception as e:
        return jsonify({'error': str(e)}), 422

    loan_id = str(uuid.uuid4())
    new_loan = {
        '_id': loan_id,
        'memberName': member_name,
        'ISBN': isbn,
        'title': book_details['title'],
        'bookID': book_details['_id'],
        'loanDate': loan_date
    }
    mongo.db.loans.insert_one(new_loan)
    return jsonify({'loanID': loan_id}), 201

@loan_bp.route('/', methods=['GET'])
def get_loans():
    loans = list(mongo.db.loans.find())
    for loan in loans:
        loan['_id'] = str(loan['_id'])
    return jsonify(loans), 200

@loan_bp.route('/<string:loan_id>', methods=['GET'])
def get_loan(loan_id):
    loan = mongo.db.loans.find_one({'_id': loan_id})
    if loan:
        loan['_id'] = str(loan['_id'])
        return jsonify(loan), 200
    else:
        return jsonify({'error': 'Loan not found'}), 404

@loan_bp.route('/<string:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    result = mongo.db.loans.delete_one({'_id': loan_id})
    if result.deleted_count > 0:
        return jsonify({'loanID': loan_id}), 200
    else:
        return jsonify({'error': 'Loan not found'}), 404
