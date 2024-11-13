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
@student.route('/students', methods=['GET'])
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

# Display all subjects in database
@student.route('/view-subjects', methods=['GET'])
def getSubjects():
    subjects = db.mst_subject.find()

    #get list of students from collection
    subls = list(subjects)
    subjectls = popID(subls)
    print(subls)
    
    return render_template('view.html', subjects = subjectls)

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
    
@student.route('/create-student', methods=['GET', 'POST'])
def createRecord():
    if request.method == 'POST':
        data = request.get_json()
        student_name = data['studentName']
        subject_name = data['subject']
        grade = data['grade']

        # Check if the student with the same name already exists
        existing_student = db.mst_student.find_one({"student_name": student_name, "subject_name": subject_name})
        if existing_student:
            # if error occured send a error message
            return {'message': 'Student with name '+student_name+' and subject '+subject_name+' already exists!',  'category':'danger'}

        # Check if the subject exists in the subject table
        subject_collection = db.mst_subject
        existing_subject = subject_collection.find_one({"subject_name": subject_name})
        
        if existing_subject:
            subject_id = existing_subject['_id']
        else:
            new_subject = {"subject_name": subject_name}
            subject_result = subject_collection.insert_one(new_subject)
            subject_id = subject_result.inserted_id

        # Get grade val
        grade_val = calculate_remarks(grade)

        # Create the new student with the subject key
        student = {
            "student_name": student_name,
            "grade": int(grade),
            "subject_key": subject_id,
            "remarks": grade_val
        }
        student_result = db.mst_student.insert_one(student)
        return {'message': 'Sucess, Added '+student_name+'!',  'category':'success'}
    elif request.method == 'GET':
        # Handle GET request here
        return render_template('create.html')
    
@student.route('/create-subject', methods=['POST'])
def createSubRecord():
    if request.method == 'POST':
        data = request.get_json()
        subject_name = data['subjectName']

        # Check if the subject exists in the subject table
        subject_collection = db.mst_subject
        existing_subject = subject_collection.find_one({"subject_name": subject_name})
        if existing_subject:
            # if error occured send a error message
            return {'message': 'Student with name '+subject_name+' already exists!',  'category':'danger'}

        # Insert a new subject if it does not exist
        new_subject = {"subject_name": subject_name}
        subject_result = subject_collection.insert_one(new_subject)

        return {'message': 'Sucess, Added '+subject_name+'!',  'category':'success'}

@student.route('/update-student', methods=['GET', 'POST'])
def update_student():
    if request.method == 'POST':
        data = request.get_json()
        # print(data)
        # print("Oldie:", data.get('old'))
        old_data = data.get('old')
        new_data = data.get('new')
        # print(old_data)

        # First, retrieve the subject ID using the old subject name
        old_subject = db.mst_subject.find_one({'subject_name': old_data['subject_name']})
        if not old_subject:
            return {"message": "This subject does not exist!", "category": "danger"}


        # Search for the existing record
        existing_student = db.mst_student.find_one({
            'student_name': old_data['student_name'],
            'subject_key': old_subject['_id'],
            'grade': int(old_data['grade'])
        })
        print(existing_student, old_subject)

        if not existing_student:
            return {"message": "Student record not found.", "category": "danger"}
        
        # If student exists, get the new subject ID for the update
        new_subject = db.mst_subject.find_one({'subject_name': new_data['subject_name']})
        if not new_subject:
            return {"message": "New subject does not exist, create a subject record first!", "category": "danger"}

        # Get grade val
        grade_val = calculate_remarks(new_data['grade'])

        print("Updating student ID:", existing_student['_id'])
        print("New data:", {
            'student_name': new_data['student_name'],
            'subject_key': new_subject['_id'], 
            'grade': int(new_data['grade']),
            'remarks': grade_val
        })

        # Update the record with new data
        update_result = mongo.db.mst_student.update_one(
            {'_id': existing_student['_id']},
            {'$set': {
                'student_name': new_data['student_name'],
                'subject_key': new_subject['_id'], 
                'grade': int(new_data['grade']),
                'remarks': grade_val
            }}
        )

        if update_result.modified_count == 0:
            return {"message": "No changes made to the student record.", "category": "warning"}
        
        return {"message": "Student record updated successfully.", "category": "success"}
    elif request.method == 'GET':
        # Handle GET request here
        return render_template('update.html')



@student.route('/delete-student', methods=['GET', 'POST'])
def deleteRecord():
    if request.method == 'POST':
        data = request.get_json()
        print(data) 
        student_name = data['studentName']
        subject_name = data.get('subject', None)
        print(student_name, subject_name)

        # Student should exist - to delete
        existing_student = db.mst_student.find_one({"student_name": student_name})
        if not existing_student:
            # if error occured send a error message
            return {'message': 'Student with name '+student_name+' does not exist!',  'category':'danger'}

        # If only student name is provided, delete all occurrences with that name
        if not subject_name:
            result = db.mst_student.delete_many({"student_name": student_name})
            if result.deleted_count > 0:
                return {'message': 'Sucess, Deleted all records of '+student_name+'!',  'category':'success'}
            else:
                return {'message': 'Error occured',  'category':'danger'}
        else:
            # Check if the subject exists in the subject table
            subject_collection = db.mst_subject
            existing_subject = subject_collection.find_one({"subject_name": subject_name})

            if existing_subject:
                subject_id = existing_subject['_id']
                # If both student name and subject are provided, delete the specific record
                result = db.mst_student.delete_one({"student_name": student_name, "subject_key": subject_id})
                if result.deleted_count > 0:
                    return {'message': 'Sucess, Deleted a specific record of '+student_name+'!',  'category':'success'}
            else:
                return {'message': 'Subject name provided does not exist (Deleting records is case sensitive)',  'category':'danger'}
    elif request.method == 'GET':
        # Handle GET request here
        return render_template('delete.html')


def addSubjectName(studs):
    print("Going to add subject name", studs)
    for student in studs:
    # Fetch the subject using the subject_key from the student document
        print(student)
        subject = db.mst_subject.find_one({'_id': student['subject_key']})
        if subject:
            student['subject_name'] = subject['subject_name']
            student.pop('_id', None)
            student.pop('subject_key', None)
            print("Added sub name", student)
        else:
            print("no subject= ", student['subject_key'])
            return [] #no subject found - handle this better
        
    return studs

def calculate_remarks(grade):
    # Convert the grade string to an integer
    grade_int = int(grade)
    # Return "PASS" if the grade is 75 or higher, otherwise "FAIL"
    return "PASS" if grade_int >= 75 else "FAIL"

def popID(studs):
    for item in studs:
        item.pop('_id', None)
        
    return studs
