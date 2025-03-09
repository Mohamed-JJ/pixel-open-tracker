import requests
from send_email import GraphEmailTester
import time

def test_tracking_flow():
    # 1. First verify cloud server is ready
    print("\n1️⃣ Checking cloud server...")
    try:
        response = requests.get("https://rsc00cwwwckcw8g44kgk0k0s.develdeep.com/health")
        print(f"Server status: {'✅ Ready' if response.status_code == 200 else '❌ Not responding'}")
    except Exception as e:
        print(f"❌ Server error: {e}")
    
    # 2. Send test email
    print("\n2️⃣ Sending test email...")
    tester = GraphEmailTester()
    to_email = "dirk.tunderman@outlook.com"
    subject = f"Tracking Test {time.strftime('%Y-%m-%d %H:%M:%S')}"
    body = """
    This is a tracking test email.
    When you open this email, it should trigger the tracking pixel.
    
    Time sent: {time}
    """.format(time=time.strftime('%Y-%m-%d %H:%M:%S'))
    
    success = tester.send_test_email(to_email, subject, body)
    
    if success:
        print("\n✅ Email sent successfully!")
        print("\n3️⃣ Next steps to verify tracking:")
        print("1. Check your email inbox")
        print("2. Before opening the email, start monitoring cloud server logs:")
        print("   docker logs -f rsc00cwwwckcw8g44kgk0k0s-182842425464")
        print("3. Open the email and watch for tracking events in the logs")
        print("\n4️⃣ The tracking URL in the email will look like:")
        print("https://rsc00cwwwckcw8g44kgk0k0s.develdeep.com/track/open?uid=<message_id>&m=<email>&t=<timestamp>")
    else:
        print("\n❌ Failed to send email")

if __name__ == "__main__":
    test_tracking_flow() 