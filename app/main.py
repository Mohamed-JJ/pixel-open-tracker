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
     logging.info("Email opened!")
     print("opened images")
     return send_file(
         "./app/mjarboua.jpg",
         mimetype='image/jpg',
         as_attachment=False
     )

def send_email(to_email):
     """Send an email with a tracking pixel."""
     if (os.path.exists(path="./app/mjarboua.jpg")):
         print("file exists")
     else:
         print("file doesnt exist")

     print(os.getenv('PIXEL_URL'))
     msg = MIMEMultipart()
     msg['From'] = os.getenv('EMAIL_USER')
     msg['To'] = to_email
     msg['Subject'] = 'Test Email with Tracking'
     html = f"""
     <html>
     <body>
         <div style="background-image: url('https://feasible-firmly-monkfish.ngrok-free.app/pixel');">
             <p>Hello!</p>
             <p>This is a test email.</p>
             <img src="https://feasible-firmly-monkfish.ngrok-free.app/pixel" width="200" height="200" />
         </div>
     </body>
 </html>
     """
     msg.attach(MIMEText(html, 'html'))
     

     print(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
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
    send_email("testthisasset0x2@gmail.com")
    return jsonify({"message": "Email sent"})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=3000, debug=True)

# tracking_server.py
# import os
# from flask import Flask, request, send_file
# import json
# from datetime import datetime
# import pytz
# import logging
# import io

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)

# # 1x1 transparent GIF in bytes
# TRACKING_PIXEL = (
#     b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
#     b'\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
#     b'\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
# )

# @app.route('/')
# def home():
#     """Home page"""
#     return "Email Tracking Server is Running!"


# @app.route('/track/open')
# def track_open():
#     """Track email opens by recording pixel loads"""
#     logger.info("==========================================")
#     logger.info("Received tracking request")
#     logger.info(f"Query parameters: {request.args}")

#     try:
#         email_id = request.args.get('uid')
#         recipient = request.args.get('m')
#         timestamp = request.args.get('t')  # Added timestamp parameter

#         if not all([email_id, recipient, timestamp]):
#             logger.warning("Missing required parameters")
#             return send_tracking_pixel()

#         try:
#             # Improved file handling
#             with open('email_tracking.json', 'r') as f:
#                 tracking_data = json.load(f)
#         except (FileNotFoundError, json.JSONDecodeError):
#             tracking_data = []

#         # Find matching email record
#         email_record = next((r for r in tracking_data if r['email_id'] == email_id), None)

#         if email_record:
#             open_info = {
#                 'timestamp': datetime.now(pytz.UTC).isoformat(),
#                 'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
#                 'user_agent': request.headers.get('User-Agent', 'Unknown'),
#                 'client_type': 'Proxy' if 'google' in request.headers.get('User-Agent', '').lower() else 'Direct'
#             }
#             email_record['opens'].append(open_info)
#             logger.info(f"📩 Tracked open for email {email_id}")
            
#             # Save updated data
#             with open('email_tracking.json', 'w') as f:
#                 json.dump(tracking_data, f, indent=2)
#         else:
#             logger.warning(f"Email ID {email_id} not found in tracking records")

#         return send_tracking_pixel()

#     except Exception as e:
#         logger.error(f"Error tracking open: {str(e)}")
#         return send_tracking_pixel()


# def send_tracking_pixel():
#     """Return the tracking pixel image"""
#     response = send_file(
#         io.BytesIO(TRACKING_PIXEL),
#         mimetype='image/gif'
#     )
#     response.headers.update({
#         'Cache-Control': 'no-cache, no-store, must-revalidate',
#         'Pragma': 'no-cache',
#         'Expires': '0'
#     })
#     return response


# @app.route('/test')
# def test():
#     """Test endpoint to verify server is accessible"""
#     return "Tracking server is running!"


# if _name_ == '_main_':
#     app.run(host='0.0.0.0', port=5001, debug=True)