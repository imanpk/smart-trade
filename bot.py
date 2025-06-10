import requests

# ------------------------------
# مشخصات ربات تلگرام
# ------------------------------
TELEGRAM_TOKEN = "7897271334:AAH-chPmIGh63PygjantKtDFl7NJw8MT8_E"
CHAT_ID = 110087310

# ------------------------------
# تابع ارسال پیام به تلگرام
# ------------------------------
def send_signal_message(data):
    action = data.get("action", "").upper()
    symbol = data.get("symbol", "نامشخص")
    price = data.get("price", "؟")

    emoji = "🟢" if action == "BUY" else "🔴" if action == "SELL" else "⚪"

    message = f"""
📡 سیگنال جدید:
{emoji} نوع: {action}
💰 ارز: {symbol}
💵 قیمت: {price}
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message.strip()
    }

    try:
        response = requests.post(url, json=payload)
        print("🔗 پاسخ تلگرام:", response.text)
        if response.status_code != 200:
            print("⚠️ ارسال پیام موفق نبود.")
        else:
            print("✅ پیام به تلگرام ارسال شد.")
    except Exception as e:
        print("❌ خطا در ارسال به تلگرام:", e)
