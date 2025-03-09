from flask import Flask, jsonify, send_file, request
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os, io
import base64, uuid
import smtplib
import logging, requests
import datetime
import time
import threading

# # Load environment variables
load_dotenv()

# # Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    """Root endpoint to verify server is running"""
    return jsonify({
        'status': 'online',
        'time': datetime.datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'time': datetime.datetime.now().isoformat(),
        'endpoints': {
            'tracking': '/track/open',
            'health': '/health'
        }
    })

@app.route('/track/open')
def track_open():
    """Track email opens by serving a transparent 1x1 tracking pixel"""
    try:
        uid = request.args.get('uid')
        email = request.args.get('m')
        timestamp = request.args.get('t')
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        open_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"""
📨 Email Open Detected!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 Email ID: {uid}
👤 Recipient: {email}
⏰ Open Time: {open_time}
🌐 User Agent: {user_agent}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        print(message)
        logger.info(f"Email opened - UID: {uid}, Email: {email}, Time: {open_time}, UA: {user_agent}")
        
        # Create transparent 1x1 GIF
        transparent_gif = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        
        return send_file(
            io.BytesIO(transparent_gif),
            mimetype='image/gif',
            as_attachment=False
        )
    except Exception as e:
        logger.error(f"Error tracking open: {e}")
        return "Error", 500

def check_image(image_path):
    """
    Check if an image file exists at the specified path.
    
    This function verifies the existence of a file at the given path, typically
    used to confirm if an image file is available before processing it.
    
    Parameters:
        image_path (str): The absolute or relative file path to the image to check.
    
    Returns:
        int: 1 if the file exists at the specified path, 0 if it does not exist.
    
    Example Usage:
        if check_image('/path/to/my_image.jpg'):
            # Process the image
        else:
            # Handle missing image case
    """
    if (os.path.exists(path=image_path)):
        return 1
    else:
        return 0

def generate_random_uuid():
    return str(uuid.uuid4())

def send_email(to_email):
   """
   Send an email with an embedded tracking pixel to track when it's opened.
   
   This function creates and sends an HTML email that includes a 1x1 tracking pixel image.
   When the recipient opens the email, the image is loaded from the server, triggering
   the tracking_pixel endpoint which logs the open event.
   
   The function generates a unique ID for each email sent, which is included in the
   tracking pixel URL as a query parameter. This allows tracking specific email opens.
   
   Parameters:
       to_email (str): The email address of the recipient.
   
   Returns:
       None: The function doesn't return a value but logs success or failure.
   
   Raises:
       Exception: Catches and logs any exceptions that occur during the email sending process.
   
   Note:
       - Requires EMAIL_USER and EMAIL_PASS environment variables to be set.
       - Uses Gmail's SMTP server for sending emails.
       - The tracking pixel is served from a hardcoded URL (http://157.175.44.139:8080/pixel).
   
   Example Usage:
       send_email('recipient@example.com')
   """
   # a picture (optional), can be ommitted and use a GIF
   # if (check_image("<the file which you want to use>") == 0):
   #     print("file exists")
   #     return 0


   msg = MIMEMultipart()
   msg['From'] = os.getenv('EMAIL_USER') # your email that you which to use in your campaign
   msg['To'] = to_email # the receiver
   msg['Subject'] = 'Test Email with Tracking'
   # change the url of the picture to where your picture is hosted, preferrably a cloud solution like aws or google cloud run
   # the /pixel is the route from which where we serve the picture from

   # generate a random id to save in the database and send in the html body in the pixel_id
   random_id = generate_random_uuid()

   # construct the email body with the url image containing the random generated id as a url query parameter
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

def test_tracking_server():
    base_url = "https://rsc00cwwwckcw8g44kgk0k0s.develdeep.com"
    
    # Test health endpoint
    health_response = requests.get(f"{base_url}/health")
    print("\nHealth Check:")
    print(f"Status: {health_response.status_code}")
    print(f"Response: {health_response.json()}")
    
    # Test tracking endpoint
    track_response = requests.get(
        f"{base_url}/track/open",
        params={
            "uid": "test123",
            "m": "test@email.com",
            "t": str(int(time.time()))
        }
    )
    print("\nTracking Endpoint Test:")
    print(f"Status: {track_response.status_code}")
    
    return health_response.status_code == 200 and track_response.status_code == 200

if __name__ == "__main__":
    success = test_tracking_server()
    print(f"\nOverall Test Result: {'✅ Passed' if success else '❌ Failed'}")
