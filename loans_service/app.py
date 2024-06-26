from flask import Flask
from flask_pymongo import PyMongo
from .routes.routes import api_bp
from .routes.loans_routes import mongo as loans_mongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo:27017/LoansDB"
mongo = PyMongo(app)
loans_mongo.init_app(app)

app.register_blueprint(api_bp)

@app.route('/', methods=['GET'])
def index():
    return "Welcome to the Loan Service API!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)