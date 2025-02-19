from flask import Flask, jsonify, send_file
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import base64
import smtplib
import logging

# # Load environment variables
load_dotenv()

# # Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/pixel', methods=["GET"])
def tracking_pixel():
    """Track email opens by logging the event and returning a 1x1 pixel GIF."""
    logging.info("Email opened!") # print an event message that you received the signal that the email was opened
    print("opened images")
    return send_file(
        "/app/app/mjarboua.jpg",
        mimetype='image/jpg',
        as_attachment=False
    )

def send_email(to_email):
    """Send an email with a tracking pixel."""
    # a picture (optional), can be ommitted and use a GIF 
    if (os.path.exists(path="./app/mjarboua.jpg")):
        print("file exists")
        return 0
    else:
        print("file doesnt exist")
    print(os.getenv('PIXEL_URL')) # store your pixel/GIF/image url in a ENV variable
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_USER') # your email that you which to use in your campaign
    msg['To'] = to_email # the receiver
    msg['Subject'] = 'Test Email with Tracking'
    # change the picture height and width to what you prefer (1x1 pixel)
    # change the url of the picture to where your picture is hosted, preferrably a cloud solution like aws or google cloud run
    # the /pixel is the route from which where we serve the picture from
    html = f"""
    <html>
    <body>
            <p>Hello!</p>
            <p>This is a test email.</p>
            <img src="http://157.175.44.139:8080/pixel" width="200" height="200" />
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
