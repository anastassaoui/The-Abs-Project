from flask import Flask, render_template, redirect, url_for, request, g, session, abort
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, close_db
from datetime import datetime, timezone, timedelta
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)



@app.teardown_appcontext
def teardown(error):
    close_db(error)

def get_current_user():
    user_result = None
    if 'user' in session:
        user_email = session['user']
        db = get_db()
        db.execute('''SELECT id, firstname, lastname, email, password, admin
                       FROM users 
                       WHERE email = %s''', 
                       (user_email,))
        user_result = db.fetchone()
    return user_result


def check_admin():
    user = get_current_user()
    if user:
        return user['admin'] == 1
    return False



@app.route('/')
def index():
    user = get_current_user()
    return render_template('index.html', user=user)




@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        db = get_db()
        email = request.form['email']
        password = request.form['password']
        
        db.execute('''SELECT id, email, password, admin
                       FROM users
                       WHERE email = %s''', (email,))
        user_result = db.fetchone()
        
        if user_result and check_password_hash(user_result['password'], password):
            session['user'] = user_result['email']
            
            if user_result['admin']:
                return redirect(url_for('teacher'))
            else:
                return redirect(url_for('student'))
        else:
            return '<h1>The password is incorrect!</h1>'
        
    return render_template('signin.html', user=get_current_user())




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = get_db()
        hashed_password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        try:
            db.execute('''INSERT INTO users (firstname, lastname, email, password, admin)
                           VALUES (%s, %s, %s, %s, %s)''',
                       (request.form['firstname'],
                        request.form['lastname'],
                        request.form['email'],
                        hashed_password,
                        '0'))  # Default
            db.connection.commit()
            return redirect(url_for('signedup'))
        except psycopg2.IntegrityError:
            db.connection.rollback()
            return '<h1>Email already registered. Please use a different email.</h1>'
        
    return render_template('signup.html', user=get_current_user())



####################################################################

@app.route('/aboutus')
def aboutus():
    return '<h2>Add later</h2>'



@app.route('/contactus')
def contactus():
    return '<h2>Add later</h2>'

#####################################################################


@app.route('/student')
def student():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))
    return render_template('student.html', user=user)




@app.route('/attendance')
def attendance():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))
    return render_template('attendance.html', user=user)




@app.route('/historystudent')
def historystudent():
    # Get current user
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    # Fetch 
    db = get_db()
    db.execute('''SELECT date, scannedat
                  FROM presence
                  WHERE userid = %s
                  ORDER BY date DESC''', (user['id'],))
    attendance_records = db.fetchall()

    # Rendertemplate with fetched data
    return render_template('historystudent.html', user=user, attendance_records=attendance_records)




@app.route('/historyteacher')
def historyteacher():
    if not check_admin():
        return abort(403)
    
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    # Fetch attendance records joined with user details
    db = get_db()
    db.execute('''
        SELECT users.id as student_id, users.firstname, users.lastname, 
               presence.date, presence.scannedat
        FROM users
        JOIN presence ON users.id = presence.userid
        ORDER BY presence.date DESC, presence.scannedat DESC
    ''')
    attendance_records = db.fetchall()
    
    return render_template('historyteacher.html', user=user, attendance_records=attendance_records)




@app.route('/teacher')
def teacher():
    if not check_admin():
        return abort(403)
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))
    return render_template('teacher.html', user=user)



@app.route('/generate_code')
def generate_code():
    if not check_admin():
        return abort(403)

    code = str(uuid.uuid4().hex[:6].upper())

    db = get_db()
    
    db.execute('''INSERT INTO temp_codes (code, generated_at)
                   VALUES (%s, NOW())''', 
                   (code,))
    db.connection.commit()
    
    return render_template('teacher.html', code=code)



from datetime import timezone

@app.route('/process_code', methods=['POST'])
def process_code():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    code = request.form['code']
    db = get_db()
    
    db.execute('''SELECT code, generated_at
                   FROM temp_codes
                   WHERE code = %s
                   ORDER BY generated_at DESC
                   LIMIT 1''', (code,))
    code_record = db.fetchone()
    
    if code_record:
        generated_code = code_record['code']
        generated_time = code_record['generated_at']

        # If generated_time is naive, make it timezone-aware (assuming it's in UTC)
        if generated_time.tzinfo is None:
            generated_time = generated_time.replace(tzinfo=timezone.utc)

        current_time = datetime.now(timezone.utc)  #timezone-aware ma 5dmat 7ta fa9satni

        print(f"Generated Code: {generated_code}")
        print(f"Generated Time: {generated_time}")
        print(f"Current Time: {current_time}")
        print(f"Time Difference: {(current_time - generated_time).total_seconds()} seconds")

        # Check if code matches and is within the time limit
        if code == generated_code and (current_time - generated_time).total_seconds() <= 30:
            time = datetime.now(timezone.utc) + timedelta(hours=1)
            db.execute('''INSERT INTO presence (userid, date, scannedat)
                   VALUES (%s, CURRENT_DATE, %s)''',
               (user['id'], time))
            db.connection.commit()

            db.connection.commit()

            return '<h1>Code Validated Successfully! Your attendance has been recorded.</h1>'

    return '<h1>Invalid or Expired Code</h1>'





@app.route('/signedup')
def signedup():
    return render_template('signedup.html')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
