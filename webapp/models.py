from flask_login import UserMixin
from flask_pymongo import PyMongo

mongo = PyMongo()

from pydantic import BaseModel

class Student(BaseModel, UserMixin):
    def __init__(self, _id, name, subject, grade, remarks):
        self._id = _id
        self.student_name = name
        self.subject = subject
        self.grade = grade
        self.remarks = self.calculate_remarks(grade)

    def calculate_remarks(self, grade):
        return "PASS" if grade >= 75 else "FAIL"

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return str(self._id)
    
# class Product():
#     def __init__(self, _id, name, price, picture):
#         self._id = _id
#         self.name = name
#         self.price = price
#         self.picture = picture
