import os
import sys
import requests
from dotenv import load_dotenv

# Load local environment variables if .env file exists
load_dotenv()

# Configuration Settings
THRESHOLD = 0.01  # Triggers alert if the rate changes by 0.01 RUB or more
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Safety check to ensure credentials are set up
if not TELEGRAM_TOKEN or not CHAT_ID:
    print("Error: Missing TELEGRAM_TOKEN or CHAT_ID environment variables.")
    sys.exit(1)

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram notification pushed successfully.")
        else:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending alert: {e}")

def get_current_rate():
    url = "https://api.frankfurter.dev/v2/rate/INR/RUB"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['rate']
        else:
            print(f"API Error ({response.status_code})")
    except Exception as e:
        print(f"Error fetching data from Frankfurter: {e}")
    return None

def main():
    current_rate = get_current_rate()
    if not current_rate:
        sys.exit(1)
        
    print(f"Current Market Rate: 1 INR = {current_rate:.4f} RUB")
    
    last_rate_file = "last_rate.txt"
    last_rate = None
    
    # Read previous rate if file exists
    if os.path.exists(last_rate_file):
        with open(last_rate_file, "r") as f:
            try:
                last_rate = float(f.read().strip())
                print(f"Last Tracked Rate: 1 INR = {last_rate:.4f} RUB")
            except ValueError:
                pass

    if last_rate is not None:
        price_diff = abs(current_rate - last_rate)
        print(f"Calculated Delta: {price_diff:.4f}")
        
        # If fluctuation matches or exceeds threshold, trigger alert
        if price_diff >= THRESHOLD:
            msg = (
                f"⚠️ INR/RUB PRICE ALERT!\n\n"
                f"The exchange rate has shifted significantly.\n"
                f"• Previous: {last_rate:.4f} RUB\n"
                f"• Current: {current_rate:.4f} RUB\n"
                f"• Variance: {price_diff:.4f} RUB"
            )
            send_telegram_alert(msg)
        else:
            print("Fluctuation is inside the safe zone. No alert needed.")
    else:
        print("Initialization Run: No baseline data found. Saving current baseline rate.")

    # Always overwrite with the newest rate for the next comparison lifecycle
    with open(last_rate_file, "w") as f:
        f.write(str(current_rate))

if __name__ == "__main__":
    main()