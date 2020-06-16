from flask import Flask, render_template, request
from flaskext.mysql import MySQL
import mysql.connector as mariadb
from flask import json

# Create Flask Object
appCrime = Flask(__name__, template_folder='templates')


# Define route for Flask object
@appCrime.route('/', methods=['GET', 'POST'])

# Function to execute queries
def crimeFinder():

    # If Request Method is 'Get' then...
    if request.method == 'GET':
        return render_template("index2.html")

    # Else if Request method is 'POST' then...
    elif request.method == 'POST':
        # Establish MariaDB Connection and connect to the cluster on AWS
        mariadb_connection = mariadb.connect(user='dbmsproject', password='password', database='chicagocrime',
                                             unix_socket='/tmp/mysql.sock',
                                             host='ec2-18-189-1-4.us-east-2.compute.amazonaws.com')
        cr = mariadb_connection.cursor()

        # API call to execute the first query related to Category of selected district
        if request.form['Submit'] == 'Category':
            query1 = request.form
            district = query1['district']  # Allocate the value of selected district from the dropdown to district variable
            # SQL Query to get answer from database
            cr.execute("SELECT L.DistrictID, D.DistrictName, count(L.CrimeID) as Count, CASE WHEN count(CrimeID) > 0 and count(CrimeID) < 100000 THEN 'VERY SAFE' WHEN count(CrimeID) > 100001 and count(CrimeID) < 150000 THEN 'SAFE' WHEN count(CrimeID) > 150000 and count(CrimeID) < 180000 THEN 'MODERATELY VULNERABLE' WHEN count(CrimeID) > 180000 and count(CrimeID)<210000 THEN 'VULNERABLE' WHEN count(CrimeID) > 210000 and count(CrimeID) < 240000 THEN 'HIGHLY VULNERABLE' WHEN count(CrimeID) > 240000 and count(CrimeID) < 300000 THEN 'EXTREMELY VULNERABLE' END AS Category from Location L LEFT JOIN District D on D.DistrictID = L.DistrictID where D.DistrictName like '" + district + "%' GROUP BY DistrictID ORDER BY Count DESC")
            rows = cr.fetchall()
            data = json.dumps(rows)  # Convert the data fetched from database to JSON format
            return data  # Return the answer in JSON format

        # API call to execute the second query related to most dangerous (Crime prone) hour in selected district
        elif request.form['Submit'] == 'Hour':
            query2 = request.form
            hours = query2['hours']  # Allocate the value of selected district from the dropdown to hours variable
            # SQL Query to get answer from database
            cr.execute('select  l.DistrictID, d.DistrictName, c.Hour, count(c.Hour) as CountofCrime from Crime c, Location l, District d where c.CrimeID = l.CrimeID and l.DistrictID = d.DistrictID and d.DistrictName like "'+ hours +'" GROUP BY Hour, DistrictID, DistrictName ORDER BY CountofCrime DESC LIMIT 3')
            rows2 = cr.fetchall()
            data2 = json.dumps(rows2)  # Convert the data fetched from database to JSON format
            return data2  # Return the answer in JSON format

        # API call to execute the third query related to reporting a crime
        elif request.form['Submit'] == 'Report':
            query3 = request.form
            fullname = query3['fullname']  # Allocate the value of fullname entered in the text box to fullname variable
            district2 = query3['district2']  # Allocate the value of selected district from the dropdown to district2 variable
            crime = query3['crime']  # Allocate the value of selected type of crime from the dropdown to crime variable
            message = query3[
                'message']  # Allocate the value of entered crime description in the textarea to message variable
            # SQL Query to get answer from database
            cr.execute("INSERT into Report (FullName, District, CrimeType, Description) VALUES( %s, %s, %s, %s)",
                       (fullname, district2, crime, message))
            cr.execute("COMMIT")
            cr.execute("SELECT * from Report")
            rows3 = cr.fetchall()
            data3 = json.dumps(rows3)  # Convert the data fetched from database to JSON format
            return data3  # Return the answer in JSON format

    # If both the if conditions are not executed then...
    return render_template('index2.html')


# Running the Flask object
if __name__ == "__main__":
    appCrime.debug = True;
    appCrime.run()
