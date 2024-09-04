from flask import Flask, render_template, redirect, url_for, request, g, session, abort
import qrcode
import io
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from database import get_db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
# Dictionary to store QR code data
qr_codes = {}

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
        
    return render_template('signin.html',user = user)

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
    return render_template('signup.html',user= user)

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

@app.route('/scan')
def scan():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))  # Redirect if not signed in
    return render_template('scan.html', user=user)

@app.route('/scanned')
def scanned():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))  # Redirect if not signed in
    return render_template('scanned.html', user=user)

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

@app.route('/activate')
def activate():
    if not check_admin():
        return abort(403)  # Forbidden access
    
    # Generate a unique identifier for the QR code
    unique_id = str(uuid.uuid4())
    
    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=8,
    )
    qr.add_data(unique_id)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    # Save QR code image in memory
    img_io = io.BytesIO()
    img.save(img_io)
    img_io.seek(0)
    
    # Convert image to base64 for embedding in HTML
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    
    # Store the unique ID in the session or database for validation
    qr_codes[unique_id] = True  # Example, store in a database in a real application
    
    # Return QR code data as JSON
    return {'qr_code_data': img_base64}

@app.route('/scan/<unique_id>')
def scan_qr(unique_id):
    # Validate the QR code
    if unique_id in qr_codes:
        del qr_codes[unique_id]  # Optionally remove the QR code after scanning
        return "QR Code Validated"
    else:
        return "Invalid QR Code"

@app.route('/signedup')
def signedup():
    return render_template('signedup.html')

if __name__ == '__main__':
    app.run(debug=True)
