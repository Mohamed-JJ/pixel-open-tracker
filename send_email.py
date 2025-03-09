import requests
import uuid
import datetime
import logging
import os
import json
from dotenv import load_dotenv
from msal import ConfidentialClientApplication

logger = logging.getLogger(__name__)

class GraphEmailTester:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize credentials from environment variables
        self.client_id = os.getenv('CLIENT_ID_1')
        self.client_secret = os.getenv('SECRET_VALUE_1')  # Using SECRET_VALUE_1 as per your env file
        self.tenant_id = os.getenv('TENANT_ID_1')
        self.sender_email = os.getenv('MS365_EMAIL_1')
        self.tracking_server = "https://rsc00cwwwckcw8g44kgk0k0s.develdeep.com"
        print(self.client_id)
        print(self.client_secret)
        print(self.tenant_id)
        print(self.sender_email)
        # Initialize MSAL application
        self.app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )
        
        self.access_token = None
        
        
    def get_access_token(self):
        """Get access token from Microsoft Graph API"""
        try:
            result = self.app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                logger.info("Successfully acquired access token")
                return True
            else:
                logger.error(f"Failed to get token: {result.get('error_description')}")
                return False
                
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return False

    def send_test_email(self, to_email: str, subject: str, body: str):
        """Send a test email using Microsoft Graph API with tracking pixel"""
        
        if not self.get_access_token():
            logger.error("Failed to get access token. Cannot send email.")
            return False

        try:
            # Generate unique message ID and timestamp for tracking
            message_id = str(uuid.uuid4())
            timestamp = int(datetime.datetime.now().timestamp())
            
            # Create tracking pixel URL with parameters
            tracking_pixel_url = f"{self.tracking_server}/track/open?uid={message_id}&m={to_email}&t={timestamp}"
            
            # Let's log the URL to verify it
            print("\n🔍 Tracking Details:")
            print(f"Message ID: {message_id}")
            print(f"Tracking URL: {tracking_pixel_url}")
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="padding: 20px;">
                        <p>{body}</p>
                        <!-- Tracking Pixel -->
                        <img src="{tracking_pixel_url}" 
                             style="width:1px;height:1px;display:block" 
                             width="1" 
                             height="1" 
                             alt=""
                             id="tracking_{message_id}"/>
                    </div>
                </body>
            </html>
            """
            
            # Log the complete HTML for verification
            print("\n📧 Email HTML Preview:")
            print(html_content)
            
            # Prepare email data
            email_data = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "html",
                        "content": html_content
                    },
                    "toRecipients": [{"emailAddress": {"address": to_email}}]
                },
                "saveToSentItems": "true"
            }

            # Send email using Graph API
            url = f'https://graph.microsoft.com/v1.0/users/{self.sender_email}/sendMail'
            response = requests.post(
                url, 
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                },
                json=email_data
            )
            
            if response.status_code == 202:
                logger.info(f"✅ Email sent successfully to {to_email}")
                # Save tracking information
                self._save_email_tracking_info(message_id, to_email, subject)
                return True
            else:
                logger.error(f"❌ Failed to send email. Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending email: {str(e)}")
            return False 

    def _save_email_tracking_info(self, message_id: str, recipient: str, subject: str):
        """Save email tracking information to a local JSON file"""
        tracking_data = {
            "email_id": message_id,
            "recipient": recipient,
            "subject": subject,
            "sent_time": datetime.datetime.now().isoformat(),
            "opens": []
        }
        
        try:
            filename = "email_tracking.json"
            existing_data = []
            
            # Load existing tracking data if file exists
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    existing_data = json.load(f)
            
            # Add new tracking data
            existing_data.append(tracking_data)
            
            # Save updated tracking data
            with open(filename, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
            logger.info(f"Saved tracking info for email {message_id}")
            
        except Exception as e:
            logger.error(f"Failed to save tracking info: {str(e)}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create test instance
    tester = GraphEmailTester()
    
    # Test email parameters
    to_email = "dirk.tunderman@outlook.com"  # Replace with the actual recipient email
    subject = f"Test Email with Tracking {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    body = """
    Hello!
    
    This is a test email with tracking pixel.
    
    Best regards,
    Email Tracker
    """
    
    # Send test email
    print("\n====== Starting Email Test ======")
    print(f"From: {tester.sender_email}")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    
    success = tester.send_test_email(to_email, subject, body)
    
    if success:
        print("\n✅ Test completed successfully!")
        print("The email has been sent with tracking pixel.")
        print("Check email_tracking.json for tracking information.")
    else:
        print("\n❌ Test failed!") 