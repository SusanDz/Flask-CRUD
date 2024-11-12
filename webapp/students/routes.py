from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from webapp.students import students as student
from bson.objectid import ObjectId
from pymongo import errors
import base64
from ..models import mongo
db = mongo.db

# Display all students in database
@student.route('/students', methods=['GET', 'POST'])
def getStudents():
    filter_type = request.args.get('filter', 'all')  # Default is 'all'
    if filter_type == 'pass':
        students = db.mst_student.find({"remarks": "PASS"})
    elif filter_type == 'fail':
        students = db.mst_student.find({"remarks": "FAIL"})
    else:
        students = db.mst_student.find()

    #get list of students from collection
    studentls = list(students)

    #add subject name to each student
    studentls = addSubjectName(studentls)
    print(studentls)
    
    return render_template('students.html', students = studentls)

# Search for student by name
@student.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # get name
        data = request.get_json()
        name = data['studentName']
        print(name)

        # studentls = [db.mst_student.find_one({'student_name': name})]

        student_record = db.mst_student.find({'student_name': name}) # Fetch student from the database

        #If student exists in db
        if student_record:
            print(student_record)
            student = addSubjectName(list(student_record))
            # student_data = {
            # 'student_name': student[0]['student_name'],
            # 'subject_name': student[0]['subject_name'],
            # 'grade': student[0]['grade'],
            # 'remarks': student[0]['remarks']
            # }
        else:
            student = None

    if student:
        return jsonify({'student': student})
    else:
        return jsonify({'student': None})

# Customer adds product to cart, insert product id to the users orderProducts list
# @product.route('/addProductToCart', methods=['POST'])
# def handle_button_click():
#     # get id and name of prduct to be added to cart
#     productId = request.get_json()['id']
#     productName = request.get_json()['name']

#     # add product id to current user products list
#     try:
#         result = db.users.update_one({"username": current_user.username}, {"$push": {"products": ObjectId(productId) }})

#         # if update sucessful send a success message
#         if result.matched_count == 1 and result.modified_count == 1:
#             return {'message': 'Sucess, Added '+productName+' to your cart!',  'category':'success'}

#     except (errors.PyMongoError, AttributeError) as e:   
#         # if error occured send a error message
#         return {'message': 'Failed to add '+productName+' to your cart!',  'category':'danger'}

# # get product id by searching for product by name and price
# def getProductId(name, price):
#     prod = db.products.find_one({"name": name, "price": price})
#     return prod['_id']

def addSubjectName(studs):
    for student in studs:
    # Fetch the subject using the subject_key from the student document
        subject = db.mst_subject.find_one({'subject_key': student['subject_key']})
        student['subject_name'] = subject['subject_name']
        del student['_id']

    return studs
