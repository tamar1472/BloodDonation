import logging
import flask
import mysql.connector
from datetime import datetime
import pandas as pd

# Disable Werkzeug logs in the console
logger = logging.getLogger(__name__)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.propagate = False
# Set up the logger
logging.basicConfig(filename='available_blood.log', level=logging.INFO,
                    format=f'%(asctime)s : %(message)s')

now = datetime.now()
# database connection
connection = mysql.connector.connect(host="localhost", user="tamar", passwd="123456", database="blood_donation")

cursor = connection.cursor()

alternative_dict = {'O-': [],
                    'A+': ['A-', 'O+', 'O-'],
                    'O+': ['O-'],
                    'B+': ['B-', 'O+', 'O-'],
                    'AB+': ['A-', 'A+', 'O+', 'O-', 'B-', 'B+', 'AB-'],
                    'A-': ['O-'],
                    'B-': ['O-'],
                    'AB-': ['A-', 'B-', 'O-']}


# inserting data to db
def add_text(id, name, phone, blood, donation_date):
    try:
        insert = "INSERT INTO donors (donor_id, donor_name,donor_phone, blood_type, last_donation_date, eligibility_status) VALUES (%s,%s,%s,%s,%s,%s)"
        cursor.execute(insert, (id, name, phone, blood, donation_date, "Eligible"))
        connection.commit()
        flask.flash("Blood Donation Accepted!", 'success')
        return 1, "Blood Donation Accepted!"
    except mysql.connector.Error as e:
        flask.flash(str(e), 'error')
        return 0, "ERROR:{}".format(e)


def get_data(blood, amount, request_date):
    # get from donors table
    fetch = "SELECT * FROM donors WHERE blood_type = %s and eligibility_status = 'Eligible' LIMIT %s"
    cursor.execute(fetch, (blood, amount))
    rows = cursor.fetchall()

    # if not enough amount of blood type
    if len(rows) != amount:
        available = []
        alt = "SELECT COUNT(*) FROM donors WHERE blood_type = %s and eligibility_status = 'Eligible'"
        for b in alternative_dict[blood]:
            cursor.execute(alt, (b,))
            count = cursor.fetchall()
            # check if rows in db are more or equal than the amount
            if count[0][0] >= amount:
                available.append(b)

        if not available:
            flask.flash("Not enough donations for this blood type {}".format(blood), 'error')
            return 0, "Not enough donations for this blood type {}".format(blood)
        else:
            flask.flash('Alternative blood types are: {}'.format(available), 'error')
            return 'Alternative blood types are: {}'.format(available)

    # insert to donations
    for row in rows:
        print(row)
        insert_query = "INSERT INTO donations (donation_id,donor_id,donation_date, blood_type) VALUES (DEFAULT,%s, %s, %s)"
        cursor.execute(insert_query, (row[0], request_date, row[3]))
        update_query = "UPDATE donors SET eligibility_status = 'Not Eligible' WHERE donor_id = %s and last_donation_date = %s;"
        cursor.execute(update_query, (row[0], str(row[4])))

    connection.commit()
    print(len(rows))
    for r in rows:
        print(r)
    flask.flash("Moved {} rows with blood type {}".format(min(len(rows), amount), blood), 'success')
    return 1, "Moved {} rows with blood type {}".format(min(len(rows), amount), blood)


# Multiple Casualty Incident, get only blood type O-.
def mci(amount):
    fetch = "SELECT * FROM donors WHERE blood_type = 'o-' and eligibility_status = 'Eligible' LIMIT %s"
    cursor.execute(fetch, (amount,))
    rows = cursor.fetchall()
    if len(rows) != amount:
        flask.flash("Not enough donations for this blood type O-", 'error')
        return 0, "Not enough donations for this blood type O-"

    # insert to donations
    for row in rows:
        print(row)
        insert_query = "INSERT INTO donations (donation_id,donor_id,donation_date, blood_type) VALUES (DEFAULT,%s, %s, %s)"
        cursor.execute(insert_query, (row[0], now, row[3]))  # row 4 to today date
        update_query = "UPDATE donors SET eligibility_status = 'Not Eligible' WHERE donor_id = %s and last_donation_date = %s;"
        cursor.execute(update_query, (row[0], str(row[4])))

    connection.commit()
    flask.flash("Moved {} rows with blood type O-".format(min(len(rows), amount)), 'success')
    return 1, "Moved {} rows with blood type O-".format(min(len(rows), amount))


def showTable():
    blood_type = {}
    for t in alternative_dict.keys():
        cursor.execute("SELECT COUNT(*) FROM donors WHERE eligibility_status = 'Eligible' and blood_type = %s", (t,))
        blood_type[t] = cursor.fetchall()[0][0]
    return blood_type
