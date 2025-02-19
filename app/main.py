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
    """
    Track email opens by serving a transparent 1x1 tracking pixel.
    
    This endpoint serves a transparent 1x1 GIF image that can be embedded in HTML emails
    to track when recipients open the email. When the image is loaded, this function logs
    the event and can process any pixel_id parameter passed in the query string.
    
    Request Parameters:
        pixel_id (str, optional): An identifier that can be used to associate the tracking
                                 event with a specific email or campaign.
    
    Returns:
        Response: A Flask response object containing a transparent 1x1 GIF image with
                 'image/gif' mimetype. This image is invisible to the recipient.
    
    Example Usage:
        In an HTML email: <img src="https://your-domain.com/pixel?pixel_id=campaign123" width="1" height="1" />
    """
    # Log the event that the email was opened
    logging.info("Email opened!")

    # extract the pixel_id from the query parameters, and log it for debugging
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
