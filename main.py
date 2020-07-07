import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, flash, request, redirect, url_for, session, logging
from data import Articles
from flaskext.mysql import MySQL
#from flask_mysqldb import MySQL
#import sqlalchemy as db
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.fields.html5 import DateField
from passlib.hash import sha256_crypt
from functools import wraps
from flask import make_response
from flask_wtf.csrf import CSRFProtect
from django.views.decorators.csrf import csrf_exempt

app = Flask(__name__)

#config MySQL
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = ''
#app.config['MYSQL_DB'] = 'myflaskapp'
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Init MYSQL
#mysql = MySQL(app)


#Creating Class or DictCursor
#class MySQLCursorDict(mysql.connector.cursor.MySQLCursor):
#    def _row_to_python(self, rowdata, desc=None):
#        row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
#        if row:
#            return dict(zip(self.column_names, row))
#        return None

#Using MySQL Connector
connection = mysql.connector.connect(host='localhost',
                                            database='myflaskapp',
                                            user='root',
                                            password='')

Articles = Articles()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/user', methods=['GET', 'POST'])
def user():
    return render_template('user.html')

#History
@app.route('/history')
def history():

    cur = connection.cursor()
    #Get the history details
    query_string = "SELECT * FROM payment WHERE username = %s"
    cur.execute(query_string, (session['username'],))        
    tempOfHistory = cur.fetchall()
    if tempOfHistory == []:
        print("None")
        flash('There are no transcation yet','warning')
        return redirect(url_for('dashboard'))

    tempHistory = []
    for i in range(len(tempOfHistory)):
        tempHistory.append(tempOfHistory[i])
    print("Session History")
    session['history'] = tempHistory
    print(session['history'][0][6])
    #print(tempHistory)
    #Commit to DB
    connection.commit()
    #Close COnnection
    cur.close()

    return render_template('history.html', tempHistory = tempHistory)

#sHistory
@app.route('/history/<string:id>/')
def shistory(id):
    print(id)
    for i in range(len(session['history'])):
        if id == str(session['history'][i][0]):
            id = session['history'][i]
            break
    return render_template('shistory.html', id=id)

#Edit Validation
class EditForm(Form):
    Address = StringField('Address', [validators.Length(min=1, max=50)])
    PhoneNumber = StringField('Phone Number', [validators.Length(min=10, max=10)]) 
    #Birthdate = DateField('Birthdate', format='%d-%m-%Y')
    Airtel_PhoneNumber = StringField('Airtel Phone Number', [validators.Length(min=10, max=10)])
    PGVCL = StringField('PGVCL Consumer Number', [validators.Length(min=1, max=20)])
    GAS = StringField('Gujarat Gas Consumer Number', [validators.Length(min=12, max=12)])
    d2h = StringField('Videocon D2H Id', [validators.Length(min=9, max=9)])

#Form Validation
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=20)])
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email', [validators.Length(min=6, max=30)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match')
    ])
    confirm = PasswordField('Confirm Password')

#User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #Create Cursor
        #cur= mysql.get_db('myflaskapp').cursor()

        #Using MYSQL connector
        cur = connection.cursor()

        #Execute Query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        
        #Commit to DB
        #mysql.get_db('myflaskapp').commit()

        #Commit to DB
        connection.commit()

        #Close COnnection
        cur.close()

        flash('You are now Registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


#User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get Form Field
        username = request.form['username']
        password_candidate = request.form['password']
        print(username)
        print(password_candidate)
        #Create a cursor
        cur1 = connection.cursor()

        #Get password by username
        query_string = "SELECT PASSWORD FROM users WHERE username = %s"
        cur1.execute(query_string, (username,))
        data = cur1.fetchone()
        print(data)

        
        if data != None:
            #GET stroed hash
            password = data

            #Get the User Name
            query_string = "SELECT name FROM users WHERE username = %s"
            cur1.execute(query_string, (username,))
            name = cur1.fetchone()
            print(name[0])

            #Get Email id
            query_string1 = "SELECT email FROM users WHERE username = %s"
            cur1.execute(query_string1, (username,))
            email = cur1.fetchone()
            print(email)

            #Get the user Id from cid Table
            query_string2 = "SELECT username FROM cid WHERE username = %s"
            cur1.execute(query_string2, (username,))
            cuser = cur1.fetchone()

            #compare the passord
            if sha256_crypt.verify(password_candidate, password[0]):
                
                #app.logger.info('PASSWORD MATCHED')
                #Passed
                session['logged_in'] = True
                session['username'] = username
                session['name'] = name[0]
                session['email'] = email[0]
                
                if cuser !=None:
                    #Get user by username
                    query_string = "SELECT * FROM cid WHERE username = %s"
                    cur1.execute(query_string, (session['username'],))
                    temp = cur1.fetchall()
                    #session['old_airtel'] = temp[0][1]
                    #session['old_pgvcl'] = temp[0][2]
                    #ession['old_d2h'] = temp[0][3]
                    #session['old_gas'] = temp[0][4]
                    
                    #Using Single List
                    tempOldNumberList = []
                    for i in range(len(temp[0])):
                        tempOldNumberList.append(temp[0][i])
                    print("Session NEW LIST")
                    session['cid'] = tempOldNumberList
                    print(session['cid'])

                    #User Details
                    query_string = "SELECT * FROM user_details WHERE username = %s"
                    cur1.execute(query_string, (session['username'],))
                    tempDetails = cur1.fetchall()
                    if tempDetails != []:
                        session['address'] = tempDetails[0][1]
                        session['phone_number'] = tempDetails[0][2]

                
                else:
                    session['cid'] = None

                flash('You are now Logged in', 'primary')
                return redirect(url_for('dashboard'))

            else:
                error = 'Invalid Login'
                return render_template('login.html', error=error)

            #Connection Closed
            cur.close()

        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

#Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#User
@app.route('/editUser', methods=['GET', 'POST'])
@is_logged_in
def editUser():
    form = EditForm(request.form)
    if request.method == 'POST' and form.validate():
        address = form.Address.data
        phoneNumber = form.PhoneNumber.data
        #bdate = form.Birthdate.data
        airtel = form.Airtel_PhoneNumber.data
        pgvcl = form.PGVCL.data
        gas = form.GAS.data
        d2h=form.d2h.data

        #Using MYSQL connector
        cur = connection.cursor()

        #Get user by username
        query_string = "SELECT username FROM cid WHERE username = %s"
        cur.execute(query_string, (session['username'],))
        tempUser = cur.fetchone()
        
        if(tempUser == None):
            #Execute Query First Time Insert
            cur.execute("INSERT INTO cID(username, airtel, pgvcl, d2h, gas) VALUES(%s, %s, %s, %s, %s)", (session['username'], airtel, pgvcl, d2h, gas))
            cur.execute("INSERT INTO maramount(username, airtel, pgvcl, d2h, gas) VALUES(%s, %s, %s, %s, %s)", (session['username'], 0, 0, 0, 0))
            cur.execute("INSERT INTO user_details(username, address, phone_number) VALUES(%s, %s, %s)", (session['username'], 0, 0))


        elif (tempUser[0] == session['username']):
            #Update Query
            cur.execute("UPDATE cID SET airtel=%s, pgvcl=%s, d2h=%s, gas=%s WHERE username=%s", (airtel, pgvcl, d2h, gas, session['username']))
            cur.execute("UPDATE user_details SET address=%s, phone_number=%s WHERE username=%s", (address, phoneNumber, session['username']))

        #Update the session Value Also
        query_string = "SELECT * FROM cid WHERE username = %s"
        cur.execute(query_string, (session['username'],))
        temp = cur.fetchall()
        #session['old_airtel'] = temp[0][1]
        #session['old_pgvcl'] = temp[0][2]
        #session['old_d2h'] = temp[0][3]
        #session['old_gas'] = temp[0][4]      
        
        #Using List in session
        tempOldNumberList = []
        for i in range(len(temp[0])):
            tempOldNumberList.append(temp[0][i])
        print("Session NEW LIST")
        session['cid'] = tempOldNumberList
        print(session['cid'])

        #User Details
        query_string = "SELECT * FROM user_details WHERE username = %s"
        cur.execute(query_string, (session['username'],))
        tempDetails = cur.fetchall()
        session['address'] = tempDetails[0][1]
        session['phone_number'] = tempDetails[0][2]

        #Commit
        connection.commit()

        #Close COnnection
        cur.close()
        flash('Update Successfully','success')
    return render_template('editUser.html', form=form)

#DashBoard
@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():

    if request.method == 'POST':
        if session['cid'] == None:
            flash('Enter the Edit Details first', 'danger')
            return redirect(url_for('editUser'))

        else:
            #Using MYSQL connector
            cur = connection.cursor()

            #Get Amount from maramount
            query_string = "SELECT * FROM maramount WHERE username = %s"
            cur.execute(query_string, (session['username'],))
            tempOfMar = cur.fetchone()
            tempMarchAmount = []
            for i in range(len(tempOfMar)):
                tempMarchAmount.append(tempOfMar[i])
            print("Session March NEW LIST")
            session['MarchAmount'] = tempMarchAmount

            checklist = request.form.getlist('selectNbills')
            print(checklist)
            if len(checklist) >= 1:
                session['boolCheck'] = 1
                session['lenCheck'] = len(checklist)
                session['sumOfBill'] = 0
                tempList = []
                tempGenerateBillNumber = []
                tempGenerateBillAmount = []
                SumOfSelectedBills = 0

                for i in range(len(checklist)):
                    tempList.append(checklist[i])
                    if(checklist[i] == 'airtel'):
                        tempGenerateBillNumber.append(session['cid'][1])
                        tempGenerateBillAmount.append(session['MarchAmount'][1])
                        SumOfSelectedBills = SumOfSelectedBills + session['MarchAmount'][1]

                    if(checklist[i] == 'pgvcl'):
                        tempGenerateBillNumber.append(session['cid'][2])
                        tempGenerateBillAmount.append(session['MarchAmount'][2])
                        SumOfSelectedBills = SumOfSelectedBills + session['MarchAmount'][2]

                    if(checklist[i] == 'd2h'):
                        tempGenerateBillNumber.append(session['cid'][3])
                        tempGenerateBillAmount.append(session['MarchAmount'][3])
                        SumOfSelectedBills = SumOfSelectedBills + session['MarchAmount'][3]

                    if(checklist[i] == 'gas'):
                        tempGenerateBillNumber.append(session['cid'][4])
                        tempGenerateBillAmount.append(session['MarchAmount'][4])
                        SumOfSelectedBills = SumOfSelectedBills + session['MarchAmount'][4]
                
                #Generate Bills
                session['GenerateBills'] = tempList
                session['GenerateBillNumbers'] = tempGenerateBillNumber
                session['GenerateBillAmount'] = tempGenerateBillAmount
                session['GenerateBillDate'] = 0
                session['TotalSelectedBillAmount'] = SumOfSelectedBills
            
            else:
                flash('Select the bill first', 'warning')
        
    return render_template('dashboard.html')


#Payment
@app.route('/payment', methods=['GET', 'POST'])
@is_logged_in
@csrf_exempt
def payment():

    if request.method == 'POST':
        print("HERE")
        print(session['GenerateBills'])
        print(session['GenerateBillNumbers'])
        print(session['GenerateBillAmount'])
        print(session['GenerateBillDate'])
        print(session['TotalSelectedBillAmount'])
        temp_airtel=0
        temp_gas=0
        temp_pgvcl=0
        temp_d2h=0
        for i in range(len(session['GenerateBills'])):
            print(i)
            if session['GenerateBills'][i] == "airtel":
                print("airtel")
                temp_airtel = session['GenerateBillAmount'][i]
            if session['GenerateBills'][i] == "pgvcl":
                print("pg")
                temp_pgvcl = session['GenerateBillAmount'][i]
            if session['GenerateBills'][i] == "gas":
                print("gas")
                temp_gas = session['GenerateBillAmount'][i]
            if session['GenerateBills'][i] == "d2h":
                print("d2h")
                temp_d2h = session['GenerateBillAmount'][i]
        print(temp_airtel)
        print(temp_d2h)
        print(temp_pgvcl)
        print(temp_gas)
       
        cur = connection.cursor()

        #Execute Query
        cur.execute("INSERT INTO payment(username, airtel, pgvcl, d2h, gas, total) VALUES(%s, %s, %s, %s, %s, %s)", (session['username'], temp_airtel, temp_pgvcl, temp_d2h, temp_gas, session['TotalSelectedBillAmount']))
        
        #Commit to DB
        connection.commit()

        #Close COnnection
        cur.close()
        flash('Payment Confirm', 'success')
        return redirect(url_for('history'))
    param_dict = {
            'MID':'hpetuG59424707212098',
            'ORDER_ID': session['TotalSelectedBillAmount'],
            'TXN_AMOUNT':'1',
            'CUST_ID': session['email'],
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	    'CALLBACK_URL':'http://127.0.0.1:5000/payment/',
    }
    return render_template('payment.html', param_dict=param_dict)


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)