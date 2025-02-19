from flask import Flask, jsonify, send_file, request
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os, io
import base64, uuid
import smtplib
import logging, requests

# # Load environment variables
load_dotenv()

# # Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/pixel', methods=["GET"])
def tracking_pixel():
    """Track email opens by logging the event and returning a 1x1 transparent GIF."""
    logging.info("Email opened!")  # Log the event that the email was opened
    print("opened images")
    pixel_id = request.args.get("pixel_id")
    logging.info(f"the arguments in the img request is this :{pixel_id}")
    # Create a transparent 1x1 GIF in memory
    transparent_gif = b'GIF89a\x01\x01\x80\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF,\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00;'
    # here do the changes you want like changing the variable from false to true
    
    ############################################################################
    return send_file(
        # (image path if you want to use images)
        io.BytesIO(transparent_gif), # can be removed (making the binary in file format to work eith the send_file function)
        mimetype='image/gif',
        as_attachment=False
    )

def check_image(image_path):
    if (os.path.exists(path=image_path)):
        return 1
    else:
        return 0

def generate_random_uuid():
    return str(uuid.uuid4())

def send_email(to_email):
    """Send an email with a tracking pixel."""
    # a picture (optional), can be ommitted and use a GIF
    # if (check_image("<the file which you want to use>") == 0):
    #     print("file exists")
    #     return 0
    # else:
    #     print("file doesnt exist")


    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_USER') # your email that you which to use in your campaign
    msg['To'] = to_email # the receiver
    msg['Subject'] = 'Test Email with Tracking'
    # change the url of the picture to where your picture is hosted, preferrably a cloud solution like aws or google cloud run
    # the /pixel is the route from which where we serve the picture from

    # generate a random id to save in the database and send in the html body in the pixel_id
    random_id = generate_random_uuid()
    html = f"""
    <html>
    <body>
            <p>Hello!</p>
            <p>This is a test email.</p>
            <img src="http://157.175.44.139:8080/pixel?pixel_id={random_id}" width="1" height="1" />
    </body>
 </html>
    """
    msg.attach(MIMEText(html, 'html'))
     

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
            server.send_message(msg)
        logging.info(f"Email sent to {to_email}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

@app.route("/track", methods=['GET'])
def track():
    """Endpoint to trigger email sending."""
    if (send_email("simojarboue28@gmail.com") == 0):
        return jsonify({"status": "fail", "message": "no picture is available"}) 
    return jsonify({"message": "Email sent"})
