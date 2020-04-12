# from flask import Flask, render_template
# import datetime
# import re
# application = Flask(__name__)

# @application.route("/")
# def home():
#     #print('s')
#     return render_template('index.html')

from flask import Flask, render_template,request, url_for, redirect, session
from datetime import datetime
from flask_mysqldb import MySQL
import MySQLdb.cursors
import datetime
import re
application = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
application.secret_key = 'ZoomTravel'

# Enter your database connection details below
application.config['MYSQL_HOST'] = 'flaskapp.crmt6c0dobbu.us-east-2.rds.amazonaws.com'
application.config['MYSQL_USER'] = 'team13'
application.config['MYSQL_PASSWORD'] = 'team132020'
application.config['MYSQL_PORT'] = 3306
application.config['MYSQL_DB'] = 'flaskapp'

# Intialize MySQL
mysql = MySQL(application)

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/signin/protips', methods=['GET', 'POST'])
def protips():
    if 'loggedin' in session:
        return render_template('protips.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login_form'))

@application.route('/signin/addTrips/', methods=['GET', 'POST'])
def addTrips():
    if 'loggedin' in session:
    # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM flights")
        records = cursor.fetchall()
        # Show the profile page with account info
        return render_template('addTrips.html', len = len(records), records = records)
    # User is not loggedin redirect to login page
    return redirect(url_for('login_form'))

@application.route('/signin/addTrips/', methods=['GET', 'POST'])
def trips_submit():
    msg = ''
    msg_type = ''
    class_type = ''
    if request.method == 'POST' and 'typeoftravel' in request.form  and 'fligtno' in request.form and 'origin' in request.form and 'destination' in request.form and 'doj' in request.form and 'toj' in request.form:
        #defined variables
        typeoftravel = request.form['typeoftravel']
        fligtno = request.form['fligtno']
        origin = request.form['origin']
        destination = request.form['destination']
        doj = datetime.datetime.strptime(doj, "%Y-%m-%d")
        gender = request.form['gender']
        passport = request.form['passport']
        country = request.form['country']
       
        #connection to Database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE traveler_record SET name = %s, gender = %s, DOB = %s, passport_num = %s, country_of_res = %s where email = %s', (name,gender,formatted_date,passport,country,email,))
        mysql.connection.commit()
        msg = 'Profile Updated!'
        msg_type = 'Success'
        class_type = 'happyFlappy'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        msg_type = 'Error'
        class_type = 'sadFlappy'
    # Show registration form with message (if any)
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
    record = cursor.fetchone()
    # Show the profile page with account info
    return render_template('trips.html', record=record)


@application.route('/about')
def aboutUs():
    return render_template('about-us.html')

@application.route('/contactUs')
def contactUs():
    return render_template('about-us.html', msg="contactUs")

@application.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error.html'), 404

@application.route('/signin', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        return redirect(url_for('index'))
    # show the form, it wasn't submitted
    return render_template('Login.html',sType="signIn")

@application.route('/signup', methods=['GET', 'POST'])
def signup_form():
    if request.method == 'POST':
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('Login.html',sType="signUp")


@application.route('/signin/', methods=['GET', 'POST'])
def signin_auth():
    # if request.method == 'POST':
    #     return redirect(url_for('index'))
    msg = ''
    msg_type = ''
    class_type = ''
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
            return redirect(url_for('home', account=account['name']))
    
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Hmmm, the information you entered does not match our records. Please try again!'
            msg_type = 'Error'
            class_type = 'sadFlappy'
    return render_template('Login.html', msg=msg, msg_type=msg_type,sType="signIn", class_type=class_type)

@application.route('/signin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        print(request.args.get('account'))
        return render_template('home.html', account=request.args.get('account'))
    # User is not loggedin redirect to index page
    return redirect(url_for('index'))

@application.route('/signup/', methods=['GET', 'POST'])
def signup_save():
    msg = ''
    msg_type = ''
    class_type = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Hmm, I think you already are a Zoomer. Please try logging in again!! '
            msg_type = 'Error'
            class_type = 'sadFlappy'
        elif not name or not password or not email:
            msg = 'Looks like the sky is empty! Please fill out the form!'
            msg_type = 'Error'
            class_type = 'sadFlappy'
        # elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        #     msg = 'Hmmm, I see that you are entering the wrong email address. Could you try changing it and try once again'
        #     msg_type = 'Error'
        #     class_type = 'sadFlappy'
        else:
            cursor.execute('INSERT INTO traveler_record (name, email, password) VALUES (%s, %s, %s)', (name, email, password,))
            mysql.connection.commit()
            msg = 'Yippe!! You just subscribed for an easy travel. You are all set to fly high'
            msg_type = 'Success'
            class_type = 'happyFlappy'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        msg_type = 'Error'
        class_type = 'sadFlappy'
    # Show registration form with message (if any)
    return render_template('Login.html', msg=msg, msg_type=msg_type, class_type=class_type)

@application.route('/profile', methods=['GET', 'POST'])
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

@application.route('/profile/', methods=['GET', 'POST'])
def profile_submit():
    msg = ''
    msg_type = ''
    class_type = ''
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
        class_type = 'happyFlappy'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        msg_type = 'Error'
        class_type = 'sadFlappy'
    # Show registration form with message (if any)
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
    record = cursor.fetchone()
    # Show the profile page with account info
    return render_template('profile.html', record=record, msg=msg, msg_type=msg_type, class_type=class_type)

@application.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('email', None)
   # Redirect to index page
   return redirect(url_for('index'))

if __name__ == '__main__':
  
    application.run()