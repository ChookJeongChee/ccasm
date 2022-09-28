from flask import Flask, render_template, request
from datetime import datetime, timedelta
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

#Homepage
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('HomePage.html')

#about us
@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('AboutUs.html')

#Add employee
@app.route("/addemp", methods=['GET','POST'])
def AddEmploy():
    return render_template('AddEmploy.html')


#Add employee output
@app.route("/addempop", methods=['POST'])
def AddEmployOutput():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']



    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, emp_image_file_name_in_s3))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmployOutput.html', name=emp_name)


#Search
@app.route("/search")
def searchemp():
    return render_template('Search.html')

#SearchOutput
@app.route("/search/output", methods=['GET','POST'])
def searchempOutput():

    emp_id = request.form['emp_id']
    getRowRecord = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    if((cursor.execute(getRowRecord, {'emp_id':int(emp_id)}) == '') | (cursor.execute(getRowRecord, {'emp_id':int(emp_id)}) is None)):
        return render_template('Error.html', msg=str(e))

    try:
        cursor.execute(getRowRecord, { 'emp_id': int(emp_id) })

        for result in cursor:
            print(result)

    except Exception as e:
            return str(e)
        
    finally:
        cursor.close()
    
    return render_template("SearchOutput.html",result=result)

#Update Employee
@app.route("/updateemploy")
def updateemp():
    return render_template('UpdateEmploy.html')

#Update Employee Output
@app.route("/updateemploy/output", methods=['POST'])
def updateEmpOutput():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
    update_sql = "UPDATE employee SET first_name = %(first_name)s , last_name = %(last_name)s , pri_skill = %(pri_skill)s , location = %(location)s , emp_image_file = %(emp_image_file)s WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        
        cursor.execute(update_sql, ({'first_name': first_name, 'last_name': last_name, 'pri_skill': pri_skill, 'location': location, 'emp_image_file': emp_image_file, 'emp_id': emp_id}))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Upload image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('UpdateEmployOutput.html', name=emp_name)


#Delete Employee
@app.route("/deleteemploy", methods=['GET', 'POST'])
def deleteEmp():
    return render_template('DeleteEmploy.html')

#DeleteEmployee Output
@app.route("/deleteemploy/output", methods=['POST'])
def deleteEmpOutput():

    emp_id = request.form['emp_id']

    select_sql = "SELECT emp_id FROM employee WHERE emp_id = %(emp_id)s"
    delete_statement = "DELETE FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()
    
    if(cursor.execute(select_sql, {'emp_id':int(emp_id)}) == ''):
        return render_template('Error.html', msg=str(e))
    
    try:
        cursor.execute(delete_statement, {'emp_id':int(emp_id)})

        if(cursor.execute(select_sql, {'emp_id':int(emp_id)}) == ''):
            return render_template('Error.html', msg=str(e))

        for result in cursor:
            print(result)
        
    except Exception as e:
        return render_template('Error.html', msg=str(e))
        
    finally:
        cursor.close()

    db_conn.commit()

    #Delete S3 picture
    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
    s3_client = boto3.client('s3')

    try:
        s3_client.delete_object(Bucket=custombucket, Key=emp_image_file_name_in_s3)
        return render_template("DeleteEmpOutput.html", emp_id = emp_id)

    except Exception as e:
            return str(e)

#Leave
@app.route("/leave", methods=['GET', 'POST'])
def leave():
    return render_template('AtdLeave.html')

#LeaveOutput
@app.route("/leave/output", methods=['POST'])
def leaveOutput():

    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    leave_type = request.form['leave_type']
    comment = request.form['comment']
    emp_leave_file = request.files['emp_leave_file']

    startDate = datetime.strptime(start_date, "%Y-%m-%d")
    endDate = datetime.strptime(end_date, "%Y-%m-%d")

    difference = endDate - startDate
    daysLeave = difference + timedelta(1)
    daysLeave = daysLeave.days

    insert_sql = "INSERT INTO empleave VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_leave_file.filename == "":
        return render_template('Error.html', msg = "Please select a file")

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, start_date, end_date, leave_type, comment))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        
        # Uplaod image file in S3 #
        emp_leave_file_name_in_s3 = "emp-id-" + str(emp_id) + "_leave_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_leave_file_name_in_s3, Body=emp_leave_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_leave_file_name_in_s3)

        except Exception as e:
            return str(e)

    except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AtdLeaveOutput.html', date = datetime.now(), name = emp_name, id = emp_id, ttldaysofleave = daysLeave, typeOfLeave = leave_type)  


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
