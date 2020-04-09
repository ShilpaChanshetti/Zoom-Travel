# from flask import Flask, render_template
# import datetime
# import re
# app = Flask(__name__)

# @app.route("/")
# def home():
#     #print('s')
#     return render_template('index.html')

from flask import Flask, render_template,request, url_for, redirect, session
from datetime import datetime
from flask_mysqldb import MySQL
import MySQLdb.cursors
import datetime
import re
app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'ZoomTravel'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_DB'] = 'isd'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    # return render_template('index.html')
    return render_template('testing.html')

@app.route('/about')
def aboutUs():
    return render_template('about-us.html')

@app.route('/contactUs')
def contactUs():
    return render_template('about-us.html', msg="contactUs")

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error.html'), 404

@app.route('/signin', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        return redirect(url_for('index'))
    # show the form, it wasn't submitted
    return render_template('Login.html',sType="signIn")

@app.route('/signup', methods=['GET', 'POST'])
def signup_form():
    if request.method == 'POST':
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('Login.html',sType="signUp")


@app.route('/signin/', methods=['GET', 'POST'])
def signin_auth():
    # if request.method == 'POST':
    #     return redirect(url_for('index'))
    msg = ''
    msg_type = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
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
            session['id'] = account['email']
            session['email'] = account['email']
            # User is loggedin show them the home page
            return redirect(url_for('home'))
    
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            msg_type = 'Error'
    
    return render_template('Login.html', msg=msg, msg_type=msg_type,sType="signIn")

@app.route('/signin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html')
    # User is not loggedin redirect to index page
    return redirect(url_for('index'))

@app.route('/signup/', methods=['GET', 'POST'])
def signup_save():
    msg = ''
    msg_type = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
            msg_type = 'Error'
        elif not name or not password or not email:
            msg = 'Please fill out the form!'
            msg_type = 'Error'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
            msg_type = 'Error'
        else:
            cursor.execute('INSERT INTO traveler_record (name, email, password) VALUES (%s, %s, %s)', (name, email, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            msg_type = 'Success'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        msg_type = 'Error'
    # Show registration form with message (if any)
    return render_template('Login.html', msg=msg, msg_type=msg_type)

@app.route('/profile', methods=['GET', 'POST'])
def profile_form():
    if 'loggedin' in session:
    # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
        record = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', record=record)
    # User is not loggedin redirect to login page
    return redirect(url_for('login_form'))

@app.route('/profile/', methods=['GET', 'POST'])
def profile_submit():
    msg = ''
    msg_type = ''
    if request.method == 'POST' and 'name' in request.form  and 'email' in request.form and 'dob' in request.form and 'gender' in request.form and 'passport' in request.form and 'country' in request.form:
        #defined variables
        name = request.form['name']
        email = request.form['email']
        dob = request.form['dob']
        formatted_date = datetime.datetime.strptime(dob, "%Y-%m-%d")
        gender = request.form['gender']
        passport = request.form['passport']
        country = request.form['country']
       
        #connection to Database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE traveler_record SET name = %s, gender = %s, DOB = %s, passport_num = %s, country_of_res = %s where email = %s', (name,gender,formatted_date,passport,country,email,))
        mysql.connection.commit()
        msg = 'Profile Updated!'
        msg_type = 'Success'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        msg_type = 'Error'
    # Show registration form with message (if any)
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
    record = cursor.fetchone()
    # Show the profile page with account info
    return render_template('profile.html', record=record, msg=msg, msg_type=msg_type)

if __name__ == '__main__':
    app.run()

