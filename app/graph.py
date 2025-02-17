import os
from dotenv import load_dotenv
import requests
from msal import ConfidentialClientApplication
import logging
import json
import uuid  # For generating unique email IDs
import datetime  # Add this import

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphEmailTester:
    def _init_(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize and validate credentials
        self.client_id = os.getenv('CLIENT_ID_1')
        self.client_secret = os.getenv('SECRET_VALUE_1')
        self.tenant_id = os.getenv('TENANT_ID_1')
        self.sender_email = os.getenv('MS365_EMAIL_1')
        
        # Validate required environment variables
        required_vars = {
            'CLIENT_ID_1': self.client_id,
            'SECRET_VALUE_1': self.client_secret,
            'TENANT_ID_1': self.tenant_id,
            'MS365_EMAIL_1': self.sender_email
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Update tracking server with ngrok URL
        self.tracking_server = "https://4469-187-249-93-34.ngrok-free.app"
        
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
            # Create message first to get ID
            tracking_pixel_url = f"{self.tracking_server}/track/open?uid={{message_id}}&m={to_email}&t={{timestamp}}"
            
            # TEMPLATE HTML with placeholders
            html_template = """
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="padding: 20px;">
                        <p>{body}</p>
                        <img src="{tracking_url}" 
                             style="width:0;height:0;display:block" 
                             width="0" 
                             height="0" 
                             alt=""/>
                    </div>
                </body>
            </html>
            """.format(body=body, tracking_url=tracking_pixel_url)

            # Create message with placeholder ID
            create_response = requests.post(
                f'https://graph.microsoft.com/v1.0/users/{self.sender_email}/messages',
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    "subject": subject,
                    "body": {
                        "contentType": "html",
                        "content": html_template
                    },
                    "toRecipients": [{"emailAddress": {"address": to_email}}]
                }
            )
            
            if create_response.status_code != 201:
                logger.error(f"❌ Failed to create message. Status: {create_response.status_code}")
                return False
            
            message_id = create_response.json().get('id')
            if not message_id:
                logger.error("❌ Failed to get message ID from response")
                return False

            # After getting message_id, update tracking URL
            timestamp = int(datetime.datetime.now().timestamp())
            updated_html = html_template.replace("{message_id}", message_id).replace("{timestamp}", str(timestamp))
            
            # Update message content with actual tracking URL
            update_response = requests.patch(
                f'https://graph.microsoft.com/v1.0/users/{self.sender_email}/messages/{message_id}',
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    "body": {
                        "contentType": "html",
                        "content": updated_html
                    }
                }
            )
            
            if update_response.status_code != 200:
                logger.error("❌ Failed to update message content with tracking URL")

            # Then send the updated message
            send_url = f'https://graph.microsoft.com/v1.0/users/{self.sender_email}/messages/{message_id}/send'
            send_response = requests.post(send_url, headers={
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            
            if send_response.status_code == 202:
                logger.info(f"✅ Email sent successfully to {to_email}")
                self._save_email_tracking_info(message_id, to_email, subject)
                return True
            else:
                logger.error(f"❌ Failed to send email. Status: {send_response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending email: {str(e)}")
            return False

    def _save_email_tracking_info(self, email_id: str, recipient: str, subject: str):
        """Save email tracking information to a local JSON file"""
        tracking_data = {
            "email_id": email_id,
            "recipient": recipient,
            "subject": subject,
            "sent_time": datetime.datetime.now().isoformat(),
            "opens": []
        }
        
        # Save to JSON file
        try:
            filename = "email_tracking.json"
            existing_data = []
            
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    existing_data = json.load(f)
            
            existing_data.append(tracking_data)
            
            with open(filename, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
            logger.info(f"Saved tracking info for email {email_id}")
            
        except Exception as e:
            logger.error(f"Failed to save tracking info: {str(e)}")

def main():
    # Create test instance
    tester = GraphEmailTester()
    
    # Test email parameters
    to_email = "dirk.tunderman@gmail.com"  # Changed to Outlook email
    subject = "Test Email with Tracking"
    body = """
    Hello!
    
    This is a test email sent using Microsoft Graph API with open tracking.
    
    Best regards,
    Email Tester
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

if __name__ == "__main__":
    main()