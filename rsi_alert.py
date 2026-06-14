import smtplib
from email.message import EmailMessage
import os

# --- Configuration ---
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASS = os.getenv('GMAIL_PASS')
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
            smtp.set_debuglevel(1)  # This shows the full handshake in the logs
            smtp.login(GMAIL_USER, GMAIL_PASS)
            smtp.send_message(msg)
            print("Text alert sent successfully!")
            
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to send email: {e}")

# --- RSI Logic ---
# (Assuming rsi_value is already calculated above this block)

if True:
    send_text(f"TEST ALERT: This is a test. The RSI is currently {rsi_value:.2f}")
else:
    print("RSI is within normal range, no alert sent.")
