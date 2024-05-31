from flask import Blueprint
from .book_routes import book_bp
from .rating_routes import rating_bp
from .top import top_bp
from flask_pymongo import PyMongo

api_bp = Blueprint('api', __name__)
mongo = PyMongo()

api_bp.register_blueprint(book_bp, url_prefix='/books')
api_bp.register_blueprint(rating_bp, url_prefix='/ratings')
api_bp.register_blueprint(top_bp, url_prefix='/top')