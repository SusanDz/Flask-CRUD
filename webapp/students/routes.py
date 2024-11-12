from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from webapp.students import students as student
from bson.objectid import ObjectId
from pymongo import errors
import base64
from ..models import mongo
db = mongo.db

@student.route('/', methods=['GET'])
def init():
    
    return "<h1>Test URL</h1>"

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

        student_record = db.mst_student.find({'student_name': { '$regex': name, '$options': 'i' }}) # Fetch student from the database

        #If student exists in db
        if student_record:
            studs = list(student_record)
            print(studs)
            student = addSubjectName(studs)
            print("FINAL")
            print(student)
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

def addSubjectName(studs):
    print("Yo", studs)
    for student in studs:
    # Fetch the subject using the subject_key from the student document
        print(student)
        subject = db.mst_subject.find_one({'subject_key': student['subject_key']})
        student['subject_name'] = subject['subject_name']
        student.pop('_id', None)
        print("Hi", student)
    return studs
