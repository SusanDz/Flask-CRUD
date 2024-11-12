from flask import Flask
from config import Config
from flask_login import LoginManager
from bson import ObjectId
from pymongo import MongoClient # Database connector
from .models import mongo

# Initialise the database
# client = MongoClient("mongodb+srv://dev:root@cluster0.x52x0kh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# db = client.get_database("student_db")

# print(db.mst_students.find_one())

# Following application factory pattern - setup app in a function
# This allows to create multiple instances of the same app for testing purposes
def create_app(config_class=Config):

    #Create flask application instance, __name__ var has the name of the current python module
    #So that it can find resources like the template files
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)
    # print(mongo.db)
    # for doc in mongo.db.mst_student.find():
    #     print(doc)
    # pymongo
    # print(db.products)

    # Register blueprints here
    from webapp.students import students as stud
    app.register_blueprint(stud)

    # from webapp.product_page import product_page as product
    # app.register_blueprint(product)

    # from webapp.order_page import order_page as order
    # app.register_blueprint(order)

    # Initialise login manager
    # login_manager = LoginManager()
    # login_manager.login_view = 'auth.login'
    # login_manager.login_message_category = 'error'
    # login_manager.init_app(app)

    # from .models import User

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app