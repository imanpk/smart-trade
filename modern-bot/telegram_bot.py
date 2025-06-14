from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import json
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = int(os.environ["CHAT_ID"])  # حتماً به int تبدیل کن چون به صورت string خونده می‌شه
bot = Bot(token=TELEGRAM_TOKEN)

# ذخیره سیگنال در فایل
def save_signal(data):
    signals = []
    if os.path.exists("signals.json"):
        with open("signals.json", "r") as f:
            try:
                signals = json.load(f)
            except:
                signals = []
    signals.append(data)
    signals = signals[-10:]  # فقط ۱۰ تا آخر نگه‌دار
    with open("signals.json", "w") as f:
        json.dump(signals, f)

# ارسال پیام به کاربر (از Webhook)
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
    bot.send_message(chat_id=data.get("chat_id", "شناسه_کاربر"), text=message.strip())
    save_signal(data)

# دستورات ربات
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🎉 خوش اومدی به SmartTrade Bot!\n\n/help یا /guide رو بزن برای آموزش.\n/latest برای دیدن آخرین سیگنال‌ها.")

def guide(update: Update, context: CallbackContext):
    update.message.reply_text("📘 راهنمای ربات:\n\n1. سیگنال خودکار دریافت می‌کنی\n2. /latest برای دیدن آخرین سیگنال‌ها")

def latest(update: Update, context: CallbackContext):
    if not os.path.exists("signals.json"):
        update.message.reply_text("هنوز سیگنالی ثبت نشده.")
        return

    with open("signals.json", "r") as f:
        try:
            signals = json.load(f)[-3:]
        except:
            update.message.reply_text("خطا در خواندن سیگنال‌ها!")
            return

    msg = "📈 آخرین سیگنال‌ها:\n"
    for s in signals:
        msg += f"- {s.get('action', '').upper()} | {s.get('symbol')} | {s.get('price')}\n"

    update.message.reply_text(msg.strip())

# اجرای ربات
def run_bot():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("guide", guide))
    dp.add_handler(CommandHandler("latest", latest))

    updater.start_polling()
    print("🤖 ربات در حال اجراست...")
