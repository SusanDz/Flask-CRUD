import os
class Config:
    SECRET_KEY = 'Final dissertation 2023'
    MONGO_URI = "mongodb+srv://dev:os.getenv('DB_PASSWORD')@cluster0.x52x0kh.mongodb.net/student_db?retryWrites=true&w=majority&appName=Cluster0"


    # establish connection with sqlalchemy
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///mono.db'

class TestConfig(Config):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    MONGO_URI = 'mongodb://localhost:27017/testEcom'
    #os.getenv("DEV_DATABASE_URI")
    TEMPLATES_AUTO_RELOAD: bool = True
