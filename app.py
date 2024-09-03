from flask import Flask, render_template, redirect, url_for, request, send_file
import qrcode 
import io
import uuid

app = Flask(__name__)

# Dictionary to store QR code data
qr_codes = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Add authentication logic here
        return redirect(url_for('student'))
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        # Add signup logic here
        return redirect(url_for('signedup'))
    return render_template('signup.html')

@app.route('/aboutus')
def aboutus():
    return '<h2>Add later</h2>'

@app.route('/contactus')
def contactus():
    return '<h2>Add later</h2>'

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/scanned')
def scanned():
    return render_template('scanned.html')

@app.route('/historystudent')
def historystudent():
    return render_template('historystudent.html')

@app.route('/historyteacher')
def historyteacher():
    return render_template('historyteacher.html')

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

@app.route('/activate')
def activate():
    # Generate a unique identifier for the QR code
    unique_id = str(uuid.uuid4())
    
    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(unique_id)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    # Save QR code image in memory
    img_io = io.BytesIO()
    img.save(img_io)
    img_io.seek(0)
    
    # Store the unique ID in the session or database for validation
    qr_codes[unique_id] = True  # Example, store in a database in a real application
    
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name=f"{unique_id}.png")

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
