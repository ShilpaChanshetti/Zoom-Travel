# from flask import Flask, render_template
# import datetime
# import re
# app = Flask(__name__)

# @app.route("/")
# def home():
#     #print('s')
#     return render_template('index.html')

from flask import Flask, render_template,request, url_for, redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import datetime
import re
app = Flask(__name__)


# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'ISD'

# Intialize MySQL
mysql = MySQL(app)


@app.route('/')
def index():
    #print(url_for('Login'))
    return render_template('index.html')

@app.route('/about')
def aboutUs():
    return render_template('about-us.html')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error.html'), 404

@app.route('/signup', methods=['GET', 'POST'])
def signup_form():
    #if request.method == 'POST':
        #return redirect(url_for('index'))
     msg = ''
     if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            return 'Logged in successfully!'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            return render_template('Login.html')

@app.route('/signin', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('Login.html')

if __name__ == '__main__':
    app.run()

