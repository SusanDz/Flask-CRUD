from flask import Blueprint

students = Blueprint('students', __name__)

#import routes.py so registering time routes get registered as well
from webapp.students import routes