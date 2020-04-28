# from flask import Flask, render_template
# import datetime
# import re
# application = Flask(__name__)

# @application.route("/")
# def home():
#     #print('s')
#     return render_template('index.html')

from flask import Flask, render_template,request, url_for, redirect, session, jsonify
from datetime import datetime, timedelta, date
from flask_mysqldb import MySQL
import MySQLdb.cursors
import datetime
import re
application = Flask(__name__)

# Secret Key
application.secret_key = 'ZoomTravel'

# Database connection details below
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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
        record = cursor.fetchone()
        return render_template('protips.html', record=record)
    # User is not loggedin redirect to login page
    return redirect(url_for('login_form'))

#aboutUs route
@application.route('/about')
def aboutUs():
    return render_template('about-us.html')

#contactUs route
@application.route('/contactUs')
def contactUs():
    return render_template('about-us.html', msg="contactUs")

#404 error route
@application.errorhandler(404)
def page_not_found(e):
    if 'loggedin' in session:
        print(session['id'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
        record = cursor.fetchone()
        # Show the profile page with account info
        return render_template('error.html', record=record), 404
    #expliciting setting 404 
    return render_template('error.html', record=None), 404

@application.route('/signin', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        #redirect to index if method is post or any error
        return redirect(url_for('index'))

    # show the login form with signin type
    return render_template('Login.html',sType="signIn")

@application.route('/signup', methods=['GET', 'POST'])
def signup_form():
    if request.method == 'POST':
        #redirect to index if method is post or any error
        return redirect(url_for('index'))

    # show the login form with signup type
    return render_template('Login.html',sType="signUp")


@application.route('/signin/', methods=['GET', 'POST'])
def signin_auth():
    msg = ''
    msg_type = ''
    class_type = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Variables to extract form data
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

@application.route('/admin/', methods=['GET', 'POST'])
def admin_auth():
    msg = ''
    msg_type = ''
    class_type = ''
    print("yes")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM traveler_record WHERE email = "admin@tamu.edu" AND password = "admin" ')
    # Fetch one record and return result
    account = cursor.fetchone()
    print(account['email'])
    # If account exists in accounts table in out database
    if account:
        # Create session data, we can access this data in other routes
        session['loggedin'] = True
        session['id'] = account['email']
        session['email'] = account['email']
        #fetch flight data
        cursor.execute('SELECT * FROM flights')
        flights = cursor.fetchall()
        #fetch traveler record data
        cursor.execute('SELECT * FROM traveler_record')
        travelRecords = cursor.fetchall()
        #fetch itinerary data
        cursor.execute('SELECT * FROM itinerary')
        itinerary = cursor.fetchall()
        # User is loggedin show them the home page
        return render_template('admin.html', flights=flights, travelRecords=travelRecords, itinerary=itinerary)
    return render_template('Login.html', msg=msg, msg_type=msg_type,sType="signIn", class_type=class_type)

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
    if request.method == 'POST' and ('name' in request.form and request.form['name']!='')  and ('email' in request.form and request.form['email']!='') and ('dob' in request.form and request.form['dob']!='') and ('gender' in request.form and request.form['gender']!='') and ('passport' in request.form and request.form['passport']!='') and ('country' in request.form and request.form['country']!=''):
        #defined variables
        name = request.form['name']
        email = request.form['email']
        dob = request.form['dob']
        formatted_date = datetime.datetime.strptime(dob, "%Y-%m-%d")
        gender = request.form['gender']
        passport = request.form['passport']
        country = request.form['country']
        dt = datetime.date.today()
        today = datetime.datetime.combine(dt, datetime.time())
        if (formatted_date < today):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE traveler_record SET name = %s, gender = %s, DOB = %s, passport_num = %s, country_of_res = %s where email = %s', (name,gender,formatted_date,passport,country,email,))
            mysql.connection.commit()
            msg = 'Yay! Profile is updated'
            msg_type = 'Success'
            class_type = 'happyFlappy'
        else:
            msg = 'I see that the date you entered is incorrect. Please enter past date'
            msg_type = 'Error'
            class_type = 'sadFlappy'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Uh oh! Please fill out the form!'
        msg_type = 'Error'
        class_type = 'sadFlappy'
    # Show registration form with message (if any)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
    record = cursor.fetchone()
    # Show the profile page with account info
    return render_template('profile.html', record=record, msg=msg, msg_type=msg_type, class_type=class_type)

@application.route('/upcomingTrips', methods=['GET', 'POST'])
def upcomingTrips():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
        record = cursor.fetchone()
        customer_id = record['customer_id']
        header = 'Upcoming Trips'
        #Get all trips
        cursor.execute('SELECT itinerary_id, customer_id, type_of_travel, f.flight_num, DATE_FORMAT(TripDate, "%%D %%M %%Y") TripDate, origin, destination, TIME_FORMAT(departure_time, "%%H:%%i") departure_time, TIME_FORMAT(arrival_time, "%%H:%%i") arrival_time, is_security FROM itinerary i, flights f WHERE i.flight_num = f.flight_num and customer_id = %s and i.TripDate >=Date(sysdate())', (customer_id,))
        #cursor.execute('SELECT customer_id, type_of_travel, f.flight_num, TripDate, origin, destination, departure_time, arrival_time FROM itinerary i, flights f WHERE i.flight_num = f.flight_num and customer_id = 34')
        flights = cursor.fetchall()
        #print (len(flights))
        return render_template('trips.html', record=record, flights=flights, header= header )
    # User is not loggedin redirect to login page
    print("here")
    return redirect(url_for('login_form'))

@application.route('/pastTrips', methods=['GET', 'POST'])
def pastTrips():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
        record = cursor.fetchone()
        customer_id = record['customer_id']
        header = 'Past Trips'
        #Get all trips
        cursor.execute('SELECT itinerary_id, customer_id, type_of_travel, f.flight_num, DATE_FORMAT(TripDate, "%%D %%M %%Y") TripDate, origin, destination, TIME_FORMAT(departure_time, "%%H:%%i") departure_time, TIME_FORMAT(arrival_time, "%%H:%%i") arrival_time, is_security FROM itinerary i, flights f WHERE i.flight_num = f.flight_num and customer_id = %s and i.TripDate < Date(sysdate())', (customer_id,))
        flights = cursor.fetchall()
        return render_template('trips.html', record=record, flights=flights, header=header)
    # User is not loggedin redirect to login page
    print("here")
    return redirect(url_for('login_form'))

@application.route('/addTrips', methods=['GET', 'POST'])
def addTrips():
    if 'loggedin' in session:
        # Show the profile page with account info
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
        record = cursor.fetchone()
        # Show the profile page with account info
        return render_template('addTrips.html', record=record)
    # User is not loggedin redirect to login page
    return redirect(url_for('login_form'))


@application.route('/getOrigin', methods=['GET', 'POST'])
def populateOrig():
    if 'loggedin' in session:
        typeoftravel=request.form['travelType']
        print(typeoftravel)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT distinct origin FROM flights where travel_type=%s", (typeoftravel,))
        origins = cursor.fetchall()
        return jsonify(origins)
    return redirect(url_for('login_form'))

@application.route('/getDest', methods=['GET', 'POST'])
def populateDest():
    if 'loggedin' in session:
        typeoftravel=request.form['travelType']
        origin = request.form['origin']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT distinct destination FROM flights where travel_type=%s AND origin= %s", (typeoftravel,origin,))
        destinations = cursor.fetchall()
        #return jsonify({'name':records[0]['origin']})
        return jsonify(destinations)
    return redirect(url_for('login_form'))

@application.route('/getFlightDetails', methods=['GET', 'POST'])
def populateFlightDetails():
    if 'loggedin' in session:
        origin = request.form['origin']
        destination = request.form['destination']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT flight_num, date_format(departure_time, '%%h:%%i') as departure_time FROM flights where  origin= %s AND destination = %s", (origin,destination,))
        flightDetails = cursor.fetchone()
        return jsonify(flightDetails)
    return redirect(url_for('login_form'))

@application.route('/addTrips/', methods=['GET', 'POST'])
def trip_submit():
    msg = ''
    msg_type = ''
    class_type = ''
    personal_allw = ''
    checked_allw = ''
    if request.method == 'POST' and ('typeoftravel' in request.form and request.form['typeoftravel']!='') and ('doj' in request.form and request.form['doj']!='') and ('origin' in request.form and request.form['origin']!='' ) and ('destination' in request.form and request.form['destination']!='') and ('flightno' in request.form and request.form['flightno']!='') and ('toj' in request.form and request.form['toj']!=''):
        #defined variables
        flightno = request.form['flightno']
        doj = request.form['doj']
        typeOfTravel = request.form['typeoftravel']
        formatted_date = datetime.datetime.strptime(doj, "%Y-%m-%d")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
        record = cursor.fetchone()
        customerId = record['customer_id']
        if 'Domestic' in typeOfTravel:
            personal_allw = 1
            checked_allw = 0
        else:
            personal_allw = 1
            checked_allw = 2
        cursor.execute('SELECT * FROM itinerary WHERE type_of_travel = %s AND customer_id = %s AND flight_num = %s AND TripDate = %s', (typeOfTravel,customerId,flightno,formatted_date,))
        itinerary = cursor.fetchone()
        if itinerary:
            msg = 'Hmm, I think you already added this Trip! '
            msg_type = 'Error'
            class_type = 'sadFlappy'
        else:
            cursor.execute('INSERT INTO itinerary (type_of_travel, personal_item_allw, checked_bag_allw, is_id, is_checkin_counter, is_customs, is_immigration, is_security, is_head_to_gate, is_personal_item, is_checked_bag, customer_id, flight_num, TripDate) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (typeOfTravel,personal_allw,checked_allw,'F','F','F','F','F','F','F','F',customerId,flightno,formatted_date,))
            mysql.connection.commit()
            msg = 'Yay! Your trip is sucessfully added'
            msg_type = 'Success'
            class_type = 'happyFlappy'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Uh oh! Please fill out the form!'
        msg_type = 'Error'
        class_type = 'sadFlappy'
        record=''
    #end
    return render_template('addTrips.html', record=record, msg=msg, msg_type=msg_type, class_type=class_type)

@application.route('/checklist', methods=['GET', 'POST'])
def complete_checklist():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        print(request.args.get('itineraryId'))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
        record = cursor.fetchone()
        if 'International' in request.args.get('travelType'):
            return render_template('InternationalChecklist.html', travelType=request.args.get('travelType'), itineraryId=request.args.get('itineraryId'), record=record)
        else:
            return render_template('DomesticChecklist.html', travelType=request.args.get('travelType'),itineraryId=request.args.get('itineraryId'), record=record)
    # User is not loggedin redirect to index page
    return redirect(url_for('login_form'))

@application.route('/checklistSubmit', methods=['GET', 'POST'])
def checklist_submit():
    # Check if user is loggedin
    if request.method == 'POST':
        itineraryId = request.args.get('itineraryId')
        header = 'Upcoming Trips'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if request.args.get('travelType') == 'International':
            print('inside')
            isId = request.form.get("item-2")
            isCheckinCounter = request.form.get('item-4')
            isCustoms = request.form.get('item-7')
            isImmigration = request.form.get('item-9')
            isSecurity= request.form.get('item-10')
            isHeadToGate = request.form.get('item-12')
            isPersonalItem = request.form.get('item-16')
            isCheckedBag= request.form.get('item-7')

            isCheckinCounter = 'T'
            isImmigration = 'T'
            isSecurity = 'T'
            isHeadToGate = 'T'
            isPersonalItem = 'T'

            if isId == 'on':
                isId = 'T'
            else:
                isId = 'F'

            if isCustoms == 'on':
                isCustoms = 'T'
                isCheckedBag = 'T'
            else:
                isCustoms = 'F'
                isCheckedBag = 'F'

                cursor.execute ('UPDATE itinerary set is_id = %s, is_checkin_counter = %s , is_customs = %s, is_immigration =%s , is_security= %s , is_head_to_gate=%s, is_personal_item =%s, is_checked_bag= %s where itinerary_id = %s', (isId,isCheckinCounter,isCustoms,isImmigration,isSecurity,isHeadToGate,isPersonalItem,isCheckedBag,itineraryId ))
                mysql.connection.commit()
        else:

            isId = request.form.get("item-2")
            isCheckinCounter = request.form.get('item-4')
            isSecurity= request.form.get('item-7')
            isHeadToGate = request.form.get('item-8')
            isPersonalItem = request.form.get('item-5')
            isCheckedBag= request.form.get('item-6')

            isCheckinCounter = 'T'
            isSecurity = 'T'
            isHeadToGate = 'T'
            isPersonalItem = 'T'

            if isId == 'on':
                isId = 'T'
            else:
                isId = 'F'

            if isCheckedBag == 'on':
                isCheckedBag = 'T'
            else:
                isCheckedBag = 'F'

            cursor.execute ('UPDATE itinerary set is_id = %s, is_checkin_counter = %s , is_security= %s , is_head_to_gate=%s, is_personal_item =%s, is_checked_bag= %s where itinerary_id = %s', (isId,isCheckinCounter,isSecurity,isHeadToGate,isPersonalItem,isCheckedBag,itineraryId ))
            mysql.connection.commit()
        
        cursor.execute('SELECT * FROM traveler_record WHERE email = %s', (session['id'],))
        record = cursor.fetchone()
        customer_id = record['customer_id']
        #Get all trips
        cursor.execute('SELECT itinerary_id, customer_id, type_of_travel, f.flight_num, DATE_FORMAT(TripDate, "%%D %%M %%Y") TripDate, origin, destination, TIME_FORMAT(departure_time, "%%H:%%i") departure_time, TIME_FORMAT(arrival_time, "%%H:%%i") arrival_time, is_security FROM itinerary i, flights f WHERE i.flight_num = f.flight_num and customer_id = %s and i.TripDate >=Date(sysdate())', (customer_id,))
        flights = cursor.fetchall()
        return render_template('trips.html', record=record, flights=flights, header= header)
    # User is not loggedin redirect to index page
    return redirect(url_for('login_form'))

@application.route('/signin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', account=request.args.get('account'))
    # User is not loggedin redirect to index page
    return redirect(url_for('index'))

@application.route('/logout')
def logout():
   # Remove session data
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('email', None)
   # Redirect to index page
   return redirect(url_for('index'))

if __name__ == '__main__':

    application.run()