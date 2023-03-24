from flask import Flask, render_template, request, url_for, redirect, flash
from db_operations import add_text, get_data, mci, showTable

import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'mysecretkey'
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
            add_text(id, name, phone, blood, donation_date)
            print(request.form)
            return render_template('index.html')
        else:

            amount = int(request.form["amount"])
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
        get_data(blood, amount, request_date)
        temp = showTable()
        return render_template('requests.html', output_data=temp.items())
        # return render_template('requests.html', data=dat)
    else:
        temp = showTable()
        print(temp)
        return render_template('requests.html', output_data=temp.items())


if __name__ == '__main__':
    app.run(debug=True)
