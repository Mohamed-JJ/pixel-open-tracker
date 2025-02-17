# Email Tracking System Documentation

## Overview
This application is a Flask-based email tracking system that allows you to monitor when recipients open emails by embedding a tracking pixel. The system sends HTML emails with an embedded image that makes a request to your server when opened, enabling you to track email opens.

## Features
- Email open tracking using pixel tracking
- Customizable tracking image
- Secure email sending via Gmail SMTP
- Logging system for tracking events
- Environment variable configuration
- RESTful API endpoints for sending and tracking emails

## Technical Architecture

### Dependencies
- Flask: Web framework for serving the tracking pixel and API endpoints
- python-dotenv: Loading environment variables
- smtplib: Handling email sending
- email.mime: Creating HTML emails with attachments
- logging: System event logging

### Environment Variables
The following environment variables must be configured:
```
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-email-password
PIXEL_URL=your-tracking-pixel-url
```

### API Endpoints

#### 1. Tracking Pixel Endpoint
```
GET /pixel
```
- Serves the tracking pixel image
- Logs email open events
- Returns a JPG image file

#### 2. Email Sending Endpoint
```
GET /track
```
- Triggers email sending to specified recipient
- Returns JSON confirmation message

## Core Components

### Tracking Pixel Handler
```python
@app.route('/pixel', methods=["GET"])
def tracking_pixel():
```
This endpoint serves the tracking image and logs when it's accessed, indicating an email open event.

### Email Sending Function
```python
def send_email(to_email):
```
Handles email composition and sending with the following features:
- HTML email formatting
- Embedded tracking pixel
- Gmail SMTP integration
- Error handling and logging

## Implementation Details

### Email Template
The system uses an HTML email template with an embedded tracking pixel:
```html
<img src="http://157.175.44.139:8080/pixel" width="200" height="200" />
```

### Logging
The application uses Python's built-in logging module with INFO level configuration:
- Email open events
- Email sending success/failure
- System errors

## Usage Guide

1. Set up environment variables:
   - Configure EMAIL_USER and EMAIL_PASS for Gmail access
   - Set PIXEL_URL for tracking image location

2. Place tracking image:
   - Ensure `mjarboua.jpg` exists in `/app/app/` directory
   - Or modify the path in tracking_pixel() function

3. Send tracked emails:
   - Make GET request to `/track` endpoint
   - Default recipient is hardcoded (modify as needed)

## Security Considerations

1. Email Authentication:
   - Uses Gmail SMTP with TLS encryption
   - Requires secure storage of credentials

2. Image Tracking:
   - Consider privacy implications of tracking
   - Implement appropriate data retention policies

3. Server Security:
   - Ensure proper server hardening
   - Monitor for abuse or excessive requests

## Limitations and Considerations

1. Email Client Compatibility:
   - Some email clients block images by default
   - Tracking may not work if images are disabled

2. Privacy Concerns:
   - Users should be informed about tracking
   - Comply with relevant privacy regulations

3. Gmail SMTP Limits:
   - Be aware of Gmail's sending limits
   - Consider using dedicated email service for large volumes

## Error Handling

The application includes error handling for:
- Email sending failures
- File access issues
- Server errors

Errors are logged using the logging module for debugging and monitoring.
