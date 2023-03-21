import flask
import mysql.connector

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
    insert = "INSERT INTO donors (donor_id, donor_name,donor_phone, blood_type, last_donation_date, eligibility_status) VALUES (%s,%s,%s,%s,%s,%s)"
    cursor.execute(insert, (id, name, phone, blood, donation_date, "Eligible"))
    connection.commit()
    return 1


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
            return "Not enough donations for this blood type {}".format(blood)
        else:
            flask.flash('Alternative blood types are: {}'.format(available), 'error')
            return 'Alternative blood types are: {}'.format(available)

    # insert to donations
    for row in rows:
        print(row)
        insert_query = "INSERT INTO donations (donation_id,donor_id,donation_date, blood_type) VALUES (DEFAULT,%s, %s, %s)"
        cursor.execute(insert_query, (row[0], request_date, row[3]))
        update_query = "UPDATE donors SET eligibility_status = 'Not Eligible' WHERE donor_id = %s;"
        cursor.execute(update_query, (row[0],))

    connection.commit()

    print(len(rows))
    for r in rows:
        print(r)
    flask.flash("Moved {} rows with blood type {}".format(min(len(rows), amount), blood), 'success')
    return "Moved {} rows with blood type {}".format(min(len(rows), amount), blood)


# Multiple Casualty Incident, get only blood type O-.
def mci(amount):
    fetch = "SELECT * FROM donors WHERE blood_type = 'o-' and eligibility_status = 'Eligible' LIMIT %s"
    cursor.execute(fetch, (amount,))
    rows = cursor.fetchall()
    if len(rows) != amount:
        flask.flash("Not enough donations for this blood type O-")
        return "Not enough donations for this blood type O-"

    # insert to donations
    for row in rows:
        print(row)
        insert_query = "INSERT INTO donations (donation_id,donor_id,donation_date, blood_type) VALUES (DEFAULT,%s, %s, %s)"
        cursor.execute(insert_query, (row[0], row[2], row[3]))
        update_query = "UPDATE donors SET eligibility_status = 'Not Eligible' WHERE donor_id = %s;"
        cursor.execute(update_query, (row[0],))

    connection.commit()
    flask.flash("Moved {} rows with blood type O-".format(min(len(rows), amount)))
    return "Moved {} rows with blood type O-".format(min(len(rows), amount))
