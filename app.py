import flask
from flask import Flask, render_template, request, url_for, redirect, flash
import db_operations

import logging
from logging.handlers import RotatingFileHandler
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'mysecretkey'

# Disable Werkzeug logs in the console
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.propagate = False
# Set up the logger
logging.basicConfig(filename='audit.log', level=logging.INFO,
                    format=f'%(asctime)s : %(message)s')

# handler = RotatingFileHandler('audit.log', maxBytes=10000, backupCount=1)
# handler.setLevel(logging.DEBUG)
# app.logger.addHandler(handler)
# app.logger.addHandler(logging.StreamHandler())

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
        app.logger.info("ADMIN Connected to MySQL Server")
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
                app.logger.info(
                    'ADMIN ADDED USER: Blood Donated: id = {}, name = {}, blood type = {}, donation date = {}'.format(
                        id,
                        name,
                        phone,
                        blood,
                        donation_date))
            else:
                app.logger.info(result[1])
            return render_template('index.html')
        else:
            amount = int(request.form["amount"])
            print(amount)
            result = db_operations.mci(amount)
            if result[0] == 1:
                app.logger.info('Multiple Casualty Incident, donated {} amounts of O-'.format(amount))
            else:
                app.logger.info('ERROR: Not enough O- blood')
            return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/requests', methods=["POST", "GET"])
def requests():
    if request.method == "POST":
        blood = request.form.get("blood-group")
        request_date = request.form.get("Request Date")
        amount = int(request.form.get("amount"))
        result = db_operations.get_data(blood, amount, request_date)
        temp = db_operations.showTable()
        if result[0] == 1:
            app.logger.info(
                'ADMIN REQUESTED BLOOD: blood type = {}, amount = {}'.format(blood, amount))
        else:
            app.logger.info('ERROR: Not enough blood type {}'.format(blood))
        return render_template('requests.html', output_data=temp.items())
        # return render_template('requests.html', data=dat)
    else:
        temp = db_operations.showTable()
        print(temp)
        return render_template('requests.html', output_data=temp.items())


if __name__ == '__main__':
    app.run(debug=True)
