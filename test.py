import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration (using provided values)
EMAIL_SENDER = "fazlurrahaman365@gmail.com"
EMAIL_PASSWORD = "nmernyicbtpumkgo"
EMAIL_RECIPIENT = "hoodr4096@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  

def test_send_email():
    """Tests sending a simple email using the provided configuration."""
    subject = "Test Email from Python Script"
    body = "This is a test email sent from a Python script to verify email sending functionality."

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
            server.ehlo()  # Identify ourselves to the server
            server.starttls()  # Upgrade to TLS encryption
            server.ehlo()  # Re-identify after TLS encryption
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            print("Successfully logged in.")
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
            print("Test email sent successfully!")
            return True
    except smtplib.SMTPConnectError as e:
        print(f"SMTP Connection Error: {e}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return False

if __name__ == "__main__":
    print("Running email test...")
    success = test_send_email()
    if success:
        print("Email test completed successfully.")
    else:
        print("Email test failed. Check the error messages above.")