import smtplib
from email.message import EmailMessage
import os

# --- Configuration ---
# These names now match your GitHub Secrets exactly
GMAIL_USER = os.getenv('GMAIL_ADDRESS')
GMAIL_PASS = os.getenv('GMAIL_APP_PASSWORD')
PHONE_GATEWAY = os.getenv('PHONE_GATEWAY')

def send_text(message):
    try:
        print("DEBUG: Starting email process...")
        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = "SOL RSI Alert"
        msg['From'] = GMAIL_USER
        msg['To'] = PHONE_GATEWAY
        
        print("DEBUG: Connecting to Gmail...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.set_debuglevel(1)
            smtp.login(GMAIL_USER, GMAIL_PASS)
            smtp.send_message(msg)
            print("Text alert sent successfully!")
            
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to send email: {e}")

# --- Test Logic ---
rsi_value = 25.0 

if True:
    print(f"DEBUG: RSI is {rsi_value}, triggering test email...")
    send_text(f"TEST ALERT: If you see this, the email system is working. RSI is {rsi_value:.2f}")
else:
    print("RSI is within normal range, no alert sent.")
