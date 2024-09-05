from flask import Flask, render_template, redirect, url_for, request, g, session, abort
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def get_current_user():
    """Retrieve the current user from the session."""
    user_result = None
    if 'user' in session:
        user_email = session['user']
        db = get_db()
        
        user_cur = db.execute('''SELECT id, firstname, lastname, email, password, admin
                                 FROM users 
                                 WHERE email = ?''', 
                                 [user_email])
        user_result = user_cur.fetchone()
    return user_result

def check_admin():
    """Check if the current user is an admin."""
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
    user = get_current_user()
    if request.method == 'POST':
        db = get_db()
        email = request.form['email']
        password = request.form['password']
        
        # Retrieve user details including the admin status
        user_cur = db.execute('''SELECT id, email, password, admin
                                 FROM users
                                 WHERE email = ?''',
                                 [email])
        user_result = user_cur.fetchone()
        
        if user_result and check_password_hash(user_result['password'], password):
            session['user'] = user_result['email']
            
            # Check if the user is an admin
            if user_result['admin']:
                return redirect(url_for('teacher'))
            else:
                return redirect(url_for('student'))
        else:
            return '<h1>The password is incorrect!</h1>'
        
    return render_template('signin.html', user=user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    user = get_current_user()
    if request.method == 'POST':
        db = get_db()
        hashed_password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        db.execute('''INSERT INTO users (firstname, lastname, email, password, admin)
                       VALUES (?, ?, ?, ?, ?)''',
                       [request.form['firstname'],
                        request.form['lastname'],
                        request.form['email'],
                        hashed_password,
                        '0'])  # Default admin status for new users
        
        db.commit()
        return redirect(url_for('signedup'))
    return render_template('signup.html', user=user)

@app.route('/aboutus')
def aboutus():
    return '<h2>Add later</h2>'

@app.route('/contactus')
def contactus():
    return '<h2>Add later</h2>'

@app.route('/student')
def student():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))  # Redirect if not signed in
    return render_template('student.html', user=user)

@app.route('/attendance')
def attendance():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))  # Redirect if not signed in
    return render_template('attendance.html', user=user)

@app.route('/historystudent')
def historystudent():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))  # Redirect if not signed in
    return render_template('historystudent.html', user=user)

@app.route('/historyteacher')
def historyteacher():
    if not check_admin():
        return abort(403)  # Forbidden access
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))  # Redirect if not signed in
    return render_template('historyteacher.html', user=user)

@app.route('/teacher')
def teacher():
    if not check_admin():
        return abort(403)  # Forbidden access
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))  # Redirect if not signed in
    return render_template('teacher.html', user=user)

@app.route('/generate_code')
def generate_code():
    if not check_admin():
        return abort(403)  # Forbidden access

    # Generate a random code
    code = str(uuid.uuid4().hex[:6].upper())  # 6-character random code

    db = get_db()
    
    # Insert the generated code with a timestamp
    db.execute('''INSERT INTO temp_codes (code, generated_at)
                   VALUES (?, ?)''', 
                   [code, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    db.commit()
    
    return render_template('teacher.html', code=code)




@app.route('/process_code', methods=['POST'])
def process_code():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))  # Redirect if not signed in

    code = request.form['code']
    db = get_db()
    
    # Fetch the most recent code entry from temp_codes
    code_record = db.execute('''SELECT code, generated_at
                               FROM temp_codes
                               WHERE code = ?
                               ORDER BY generated_at DESC
                               LIMIT 1''', [code]).fetchone()
    
    if code_record:
        generated_code = code_record['code']
        generated_time = datetime.datetime.strptime(code_record['generated_at'], '%Y-%m-%d %H:%M:%S')
        current_time = datetime.datetime.now()
        
        if code == generated_code and (current_time - generated_time).total_seconds() <= 15:  ####define interval here
            # Insert the attendance record with the current user id
            db.execute('''INSERT INTO presence (userid, date, scannedat)
                           VALUES (?, DATE('now'), DATETIME('now'))''',
                       [user['id']])
            db.commit()
            
            # Optionally remove the used code from temp_codes
            db.execute('''DELETE FROM temp_codes WHERE code = ?''', [code])
            db.commit()

            return '<h1>Code Validated Successfully! Your attendance has been recorded.</h1>'
    
    return '<h1>Invalid or Expired Code</h1>'



@app.route('/signedup')
def signedup():
    return render_template('signedup.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
