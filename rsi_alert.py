import os
import smtplib
import requests
import pandas as pd
from email.message import EmailMessage

# --- CONFIGURATION ---
# These will be pulled from GitHub Secrets later
GMAIL_USER = os.environ.get('GMAIL_ADDRESS')
GMAIL_PASS = os.environ.get('GMAIL_APP_PASSWORD')
PHONE_GATEWAY = os.environ.get('PHONE_GATEWAY') # Format: 1234567890@tmomail.net

def get_rsi():
    # Fetch 5-minute SOL data from Binance
    url = "https://api.binance.com/api/v3/klines?symbol=SOLUSDT&interval=5m&limit=20"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'ignore1', 'ignore2', 'ignore3', 'ignore4', 'ignore5', 'ignore6'])
    df['close'] = df['close'].astype(float)
    
    # Calculate RSI (14 period)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def send_text(message):
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = "SOL RSI Alert"
    msg['From'] = GMAIL_USER
    msg['To'] = PHONE_GATEWAY
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.send_message(msg)

current_rsi = get_rsi()
if current_rsi > 70:
    send_text(f"Alert: SOL RSI is overbought at {current_rsi:.2f}")
elif current_rsi < 30:
    send_text(f"Alert: SOL RSI is oversold at {current_rsi:.2f}")
