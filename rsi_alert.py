import smtplib
from email.message import EmailMessage
import os

# --- Configuration ---
GMAIL_USER = os.getenv('GMAIL_ADDRESS')
GMAIL_PASS = os.getenv('GMAIL_APP_PASSWORD')
PHONE_GATEWAY = os.getenv('PHONE_GATEWAY')

def send_text(message):
    try:
        print("DEBUG: Connecting to Gmail...")
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
# !!! YOU MUST ADD YOUR RSI CALCULATION CODE HERE !!!
# Example placeholder:
# rsi_value = get_rsi_calculation() 

# For now, if you don't have the calculation, you need to define rsi_value
# otherwise the script will always fail.
# Example: 
# rsi_value = 25.0 

if 'rsi_value' in locals():
    if rsi_value > 70 or rsi_value < 30:
        print(f"RSI is {rsi_value:.2f}, sending alert...")
        send_text(f"SOL RSI Alert: The RSI is currently {rsi_value:.2f}")
    else:
        print(f"RSI is {rsi_value:.2f}, no alert sent.")
else:
    print("ERROR: rsi_value was not calculated. Please add your RSI formula.")
