from flask import Flask, render_template, request, url_for, redirect, flash
from db_operations import add_text, get_data, mci

import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
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

        # cursor.close()
        # connection.close()
        # print("MySQL connection is closed")
except Error as e:
    print("Error while connecting to MySQL", e)


@app.route('/', methods=["POST", "GET"])
def index():
    print(request.method)
    if request.method == "POST":
        print(request.form)

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
        add_text(id, name, phone, blood, donation_date)
        print(request.form)

        amount = request.form["amount"]
        print(amount)
        mci(amount)
        return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/requests', methods=["POST", "GET"])
def requests():
    if request.method == "POST":
        blood = request.form.get("blood-group")
        request_date = request.form.get("Request Date")
        amount = int(request.form.get("amount"))
        dat = get_data(blood, amount, request_date)
        print(dat)
        return redirect(url_for('requests'))
        # return render_template('requests.html', data=dat)
    else:
        return render_template('requests.html')


if __name__ == '__main__':
    app.run(debug=True)
