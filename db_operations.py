import flask
import mysql.connector
from datetime import datetime
import pandas as pd

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

# def audit_donation_trail():
#     # Execute the query
#     cursor.execute("SELECT * FROM audit_donation_log ORDER BY donation_id DESC LIMIT 100;")
#     # Fetch the results
#     results = cursor.fetchall()
#     # Open a text file for writing
#     with open("audit_log.txt", "w") as f:
#         f.write("---------------audit donation log------------------\n")
#         # Write the results to the text file
#         for row in results:
#             f.write("ADMIN: %s\n" % str(row))
#
#
# def audit_donor_trail():
#     # Execute the query
#     cursor.execute("SELECT * FROM audit_donor_log ORDER BY donor_id DESC LIMIT 100;")
#     # Fetch the results
#     results = cursor.fetchall()
#     # Open a text file for writing
#     with open("audit_log.txt", "w") as f:
#         # Write the results to the text file
#         f.write("---------------audit donor log------------------\n")
#         for row in results:
#             f.write("ADMIN: %s\n" % str(row))
#

# def audit_trail():
#     donations = pd.read_sql_table('donations', con=connection)
#     donors = pd.read_sql_table('donors', con=connection)
#     latest_donations = donations.loc[donations['donation_date'] == donations['donation_date'].max()]
#     latest_donors = donors.loc[donors['last_donation_date'] == donors['last_donation_date'].max()]
#     latest_rows = pd.concat([latest_donations, latest_donors], axis=1)
#     filename = 'latest_rows_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
#     latest_rows.to_csv(filename, sep='\t', index=False)
#     connection.close()
