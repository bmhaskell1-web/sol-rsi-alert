import smtplib
from email.message import EmailMessage
import os
import yfinance as yf

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
def get_rsi():
    # 1. Fetch more data (e.g., 5 days of 5-minute data)
    # This provides enough history to "warm up" the RSI calculation
    ticker = yf.Ticker("SOL-USD")
    hist = ticker.history(period="5d", interval="5m")
    
    # 2. Calculate price changes
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    
    # 3. Use Wilder's Smoothing (Matching TradingView standard)
    # The 'ewm' function with alpha=1/14 creates the correct smoothing.
    # 'min_periods=14' is critical: it ensures we don't get a 
    # value until we have enough data to be accurate.
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # 4. Return the most recent RSI value
    return rsi.iloc[-1]

# --- Execute ---
try:
    rsi_value = get_rsi()
    print(f"Current RSI: {rsi_value:.2f}")

    if rsi_value > 70 or rsi_value < 30:
        print(f"Alert Triggered! RSI: {rsi_value:.2f}")
        send_text(f"SOL RSI Alert: The RSI is currently {rsi_value:.2f}")
    else:
        print(f"RSI is {rsi_value:.2f}, no alert sent.")
except Exception as e:
    print(f"Error calculating RSI: {e}")
