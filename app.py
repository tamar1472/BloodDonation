import csv
import io
import os

from flask import Flask, render_template, request, url_for, redirect, flash, make_response, Response
import db_operations

import logging
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'mysecretkey'

# Disable Werkzeug logs in the console
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.propagate = False

# Set up a logger for general application logging
app_logger = logging.getLogger(__name__)
app_logger.setLevel(logging.ERROR)
app_logger.propagate = False
app_file_handler = logging.FileHandler('audit.log')
app_formatter = logging.Formatter('%(asctime)s  : %(message)s')
app_file_handler.setFormatter(app_formatter)
app_logger.addHandler(app_file_handler)

# Set up a logger for blood table logging
blood_logger = logging.getLogger('blood_table')
blood_logger.setLevel(logging.ERROR)
blood_file_handler = logging.FileHandler('blood_table.log')
blood_formatter = logging.Formatter('%(asctime)s : %(message)s')
blood_file_handler.setFormatter(blood_formatter)
blood_logger.addHandler(blood_file_handler)

try:
    connection = mysql.connector.connect(user='tamar', password='123456', host='127.0.0.1', port=3306,
                                         database='blood_donation',
                                         auth_plugin='mysql_native_password')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
        app.logger.error("ADMIN Connected to MySQL Server")
        # cursor.close()
        # connection.close()
        # print("MySQL connection is closed")
except Error as e:
    print("Error while connecting to MySQL", e)


@app.route('/', methods=["POST", "GET"])
def index():
    print(request.method)
    if request.method == "POST":
        print(request.form["sub_type"])
        if request.form["sub_type"] == '0':
            id = request.form["ID"]
            print(id)
            name = request.form["name"]
            print(name)
            phone = request.form["phone"]
            print(phone)
            blood = request.form.get("blood-group")
            print(blood)
            donation_date = request.form.get("last-donation-date")
            print(donation_date)
            # saving all the values to db
            result = db_operations.add_text(id, name, phone, blood, donation_date)
            print(request.form)
            if result[0] == 1:
                app.logger.error(
                    'ADMIN ADDED USER: Blood Donated: id = {}, name = {}, blood type = {}, donation date = {}'.format(
                        id,
                        name,
                        phone,
                        blood,
                        donation_date))
            else:
                app.logger.error(result[1])
            return render_template('index.html')
        else:
            amount = int(request.form["amount"])
            print(amount)
            result = db_operations.mci(amount)
            if result[0] == 1:
                app.logger.error('Multiple Casualty Incident, donated {} amounts of O-'.format(amount))
            else:
                app.logger.error('ERROR: Not enough O- blood')
            return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/requests', methods=["POST", "GET"])
def requests():
    if request.method == "POST":
        blood = request.form.get("blood-group")
        request_date = request.form.get("Request Date")
        amount = request.form.get("amount")
        if amount is not None:
            amount = int(amount)
        else:
            amount = 0
        result = db_operations.get_data(blood, amount, request_date)
        temp = db_operations.showTable()
        if result[0] == 1:
            app_logger.error(
                'ADMIN REQUESTED BLOOD: blood type = {}, amount = {}'.format(blood, amount))
        else:
            app_logger.error('ERROR: Not enough blood type {}'.format(blood))
            blood_logger.error(temp)
        return render_template('requests.html', output_data=temp.items())
    else:
        temp = db_operations.showTable()
        blood_logger.info(temp)
        return render_template('requests.html', output_data=temp.items())


# Convert audit.log to audit.txt
if os.path.exists('audit.log'):
    with open('audit.log', 'r') as log_file:
        with open('audit.txt', 'w') as txt_file:
            txt_file.write(log_file.read())

if __name__ == '__main__':
    app.run(debug=True)

# Check if the export button was pressed
