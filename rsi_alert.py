import yfinance as yf
import pandas as pd
import os
import smtplib
from email.message import EmailMessage

# --- CONFIGURATION ---
GMAIL_USER = os.environ.get('GMAIL_ADDRESS')
GMAIL_PASS = os.environ.get('GMAIL_APP_PASSWORD')
PHONE_GATEWAY = os.environ.get('PHONE_GATEWAY')

def get_rsi(symbol, period=14):
    # Fetch data using yfinance
    data = yf.download(symbol, period="1mo", interval="15m")
    if data.empty:
        print("Failed to get data from Yahoo Finance")
        return None
    
    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

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
            smtp.set_debuglevel(1)  # This forces the logs to show everything
            smtp.login(GMAIL_USER, GMAIL_PASS)
            smtp.send_message(msg)
            print("Text alert sent successfully!")
            
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to send email: {e}")

# --- EXECUTION ---
current_rsi = get_rsi("SOL-USD")

if current_rsi is not None:
    # Handle the case where RSI might be a Series instead of a single float
    rsi_value = float(current_rsi.iloc[0]) if hasattr(current_rsi, 'iloc') else float(current_rsi)
    print(f"Current RSI is: {rsi_value:.2f}")
    
   if True:
                
      send_text(f"Alert: SOL RSI is currently {rsi_value:.2f}")
   else:
        print("RSI is within normal range, no alert sent.")
