from flask import Flask
from flask_pymongo import PyMongo
from .routes.routes import api_bp
from .routes.book_routes import mongo as books_mongo
from .routes.rating_routes import mongo as ratings_mongo
from .routes.top import mongo as top_mongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo:27017/BooksDB"
mongo = PyMongo(app)
books_mongo.init_app(app)
ratings_mongo.init_app(app)
top_mongo.init_app(app)

app.register_blueprint(api_bp)

@app.route('/', methods=['GET'])
def index():
    return "Welcome to the Book Club API!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
