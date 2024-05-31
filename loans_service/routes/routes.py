from flask import Blueprint
from .loans_routes import loan_bp
from flask_pymongo import PyMongo

api_bp = Blueprint('api', __name__)
mongo = PyMongo()

api_bp.register_blueprint(loan_bp, url_prefix='/loans')