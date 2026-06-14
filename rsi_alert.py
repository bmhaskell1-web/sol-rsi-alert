import os
import smtplib
import requests
import pandas as pd
from email.message import EmailMessage

# --- CONFIGURATION (Pulls from GitHub Secrets) ---
GMAIL_USER = os.environ.get('GMAIL_ADDRESS')
GMAIL_PASS = os.environ.get('GMAIL_APP_PASSWORD')
PHONE_GATEWAY = os.environ.get('PHONE_GATEWAY')

def get_rsi():
    # Fetch 50 candles to ensure enough data for a 14-period RSI
    url = "https://api.binance.com/api/v3/klines?symbol=SOLUSDT&interval=5m&limit=50"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to connect to Binance")
        return None
    
    data = response.json()
    if not data or len(data) < 20:
        print("Not enough data received")
        return None
        
    # Convert to DataFrame
    df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'ignore1', 'ignore2', 'ignore3', 'ignore4', 'ignore5', 'ignore6'])
    df['close'] = df['close'].astype(float)
    
    # Calculate RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

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
        print("Text alert sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# --- EXECUTION ---
current_rsi = get_rsi()

if current_rsi is not None:
    print(f"Current RSI is: {current_rsi:.2f}")
    
    # Thresholds: Trigger if RSI < 30 (oversold) or > 70 (overbought)
    if current_rsi > 70 or current_rsi < 30:
        send_text(f"Alert: SOL RSI is currently {current_rsi:.2f}")
    else:
        print("RSI is within normal range, no alert sent.")
else:
    print("Could not calculate RSI.")
