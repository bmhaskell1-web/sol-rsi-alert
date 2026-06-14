import smtplib
from email.message import EmailMessage
import os

# --- Configuration ---
GMAIL_USER = os.getenv('GMAIL_ADDRESS')
GMAIL_PASS = os.getenv('GMAIL_APP_PASSWORD')
PHONE_GATEWAY = os.getenv('PHONE_GATEWAY')

def send_text(message):
    try:
        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = "SOL RSI Alert"
        msg['From'] = GMAIL_USER
        msg['To'] = PHONE_GATEWAY
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_PASS)
            smtp.send_message(msg)
            print("Alert sent successfully!")
            
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to send email: {e}")

# --- RSI Logic ---
# (Make sure 'rsi_value' is defined correctly in your code above this block)

if rsi_value > 70 or rsi_value < 30:
    print(f"RSI is {rsi_value:.2f}, sending alert...")
    send_text(f"SOL RSI Alert: The RSI is currently {rsi_value:.2f}")
else:
    print(f"RSI is {rsi_value:.2f}, no alert sent.")
