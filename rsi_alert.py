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

# --- Scoreboard Matrix Logic ---
def calculate_indicators(df):
    # RSI Calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(com=13, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(com=13, adjust=False).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD Calculation
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Hist'] = df['MACD'] - df['Signal']
    return df

def get_element_score(rsi_val, hist_curr, hist_prev, weight):
    # RSI Scoring Rule
    if rsi_val < 30: rsi_s = -5
    elif rsi_val > 70: rsi_s = 5
    elif rsi_val < 50: rsi_s = -2
    else: rsi_s = 2
    
    # MACD Slope Scoring Rule
    if hist_curr > hist_prev:
        macd_s = 1 if hist_curr < 0 else 2
    else:
        macd_s = -1 if hist_curr > 0 else -2
        
    return (rsi_s * weight) + (macd_s * weight)

def main():
    # Fetch data frames using yfinance
    ticker = yf.Ticker("SOL-USD")
    
    df_1h = calculate_indicators(ticker.history(period="14d", interval="1h"))
    df_4h = calculate_indicators(ticker.history(period="30d", interval="1h").resample('4h').last().dropna())
    df_1d = calculate_indicators(ticker.history(period="60d", interval="1d"))
    
    # Calculate scores for both the current hour (-1) and previous hour (-2) to detect the cross
    scores = []
    for offset in [-2, -1]:
        t = df_1h.index[offset]
        price = df_1h['Close'].iloc[offset]
        
        # 1-Hour Frame (Weight x1)
        rsi_1h = df_1h['RSI'].iloc[offset]
        hist_1h = df_1h['Hist'].iloc[offset]
        hist_1h_p = df_1h['Hist'].iloc[offset-1]
        score_1h = get_element_score(rsi_1h, hist_1h, hist_1h_p, 1)
        
        # 4-Hour Frame (Weight x2)
        t_4h = df_4h.index[df_4h.index <= t][-1]
        rsi_4h = df_4h.loc[t_4h, 'RSI']
        hist_4h = df_4h.loc[t_4h, 'Hist']
        idx_4h_prev = df_4h.index.get_loc(t_4h) - 1
        hist_4h_p = df_4h['Hist'].iloc[idx_4h_prev]
        score_4h = get_element_score(rsi_4h, hist_4h, hist_4h_p, 2)
        
        # Daily Frame (Weight x4)
        t_1d = df_1d.index[df_1d.index <= t][-1]
        rsi_1d = df_1d.loc[t_1d, 'RSI']
        hist_1d = df_1d.loc[t_1d, 'Hist']
        idx_1d_prev = df_1d.index.get_loc(t_1d) - 1
        hist_1d_p = df_1d['Hist'].iloc[idx_1d_prev]
        score_1d = get_element_score(rsi_1d, hist_1d, hist_1d_p, 4)
        
        total_score = score_1h + score_4h + score_1d
        scores.append((total_score, price))
        
    prev_score, _ = scores[0]
    curr_score, curr_price = scores[1]
    
    print(f"Previous Score: {prev_score} | Current Score: {curr_score} | Live Price: ${curr_price:.2f}")
    
    # --- Threshold Crossing Triggers ---
    # 1. Crossed ABOVE +50 (Bull Regime Campaign)
    if prev_score <= 50 and curr_score > 50:
        send_text(f"🚀 SOL BULL REGIME\nScore crossed above +50!\nNow: {curr_score}\nPrice: ${curr_price:.2f}")
        
    # 2. Crossed BELOW -50 (Bear Regime Campaign)
    elif prev_score >= -50 and curr_score < -50:
        send_text(f"🚨 SOL BEAR REGIME\nScore crossed below -50!\nNow: {curr_score}\nPrice: ${curr_price:.2f}")

if __name__ == "__main__":
    main()
