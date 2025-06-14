from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import json, os
from datetime import datetime, timedelta

# =====================
# تنظیمات اولیه
# =====================
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = int(os.environ.get("CHAT_ID", "0"))  # فقط برای fallback تست
bot = Bot(token=TELEGRAM_TOKEN)

USERS_FILE = "users.json"
SIGNALS_FILE = "signals.json"
ADMIN_CHAT_ID = CHAT_ID  # فقط تو اجازه تمدید داری

# =====================
# ابزارهای کاربران
# =====================
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def find_user(chat_id, users):
    return next((u for u in users if u["chat_id"] == chat_id), None)

def find_user_by_username(username, users):
    return next((u for u in users if u["username"] == username), None)

def is_active(user):
    return user["active"] and datetime.now() <= datetime.fromisoformat(user["expires_at"])

# =====================
# ذخیره سیگنال در فایل
# =====================
def save_signal(data):
    signals = []
    if os.path.exists(SIGNALS_FILE):
        with open(SIGNALS_FILE, "r") as f:
            try:
                signals = json.load(f)
            except:
                signals = []
    signals.append(data)
    signals = signals[-10:]
    with open(SIGNALS_FILE, "w") as f:
        json.dump(signals, f)

# =====================
# ارسال سیگنال به کاربران فعال
# =====================
def send_signal_message(data):
    users = load_users()
    active_users = [u for u in users if is_active(u)]

    if not active_users:
        print("⚠️ هیچ کاربر فعالی یافت نشد.")
        return

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

    for user in active_users:
        try:
            bot.send_message(chat_id=user["chat_id"], text=message.strip())
        except Exception as e:
            print(f"❌ خطا در ارسال به {user['chat_id']}: {e}")

    save_signal(data)

# =====================
# ثبت‌نام با /start
# =====================
def start(update: Update, context: CallbackContext):
    users = load_users()
    chat_id = update.effective_chat.id
    username = update.effective_user.username or f"user_{chat_id}"

    user = find_user(chat_id, users)
    if user:
        update.message.reply_text("✅ شما قبلاً ثبت‌نام کردید.")
        return

    new_user = {
        "chat_id": chat_id,
        "username": username,
        "joined_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=3)).isoformat(),
        "active": True,
        "role": "admin" if chat_id == ADMIN_CHAT_ID else "user"
    }
    users.append(new_user)
    save_users(users)

    update.message.reply_text("🎉 ثبت‌نام شدی!\n۳ روز اشتراک رایگان فعال شد.")

# =====================
# تمدید اشتراک با /extend فقط برای ادمین
# =====================
def extend(update: Update, context: CallbackContext):
    sender_id = update.effective_chat.id
    if sender_id != ADMIN_CHAT_ID:
        update.message.reply_text("⛔ فقط مدیر می‌تونه این دستور رو اجرا کنه.")
        return

    if len(context.args) != 1:
        update.message.reply_text("❌ فرمت اشتباه. مثلا بزن:\n/extend username")
        return

    username = context.args[0].lstrip("@")  # حذف @
    users = load_users()
    user = find_user_by_username(username, users)

    if not user:
        update.message.reply_text(f"❌ کاربری با نام {username} پیدا نشد.")
        return

    user["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
    user["active"] = True
    save_users(users)

    update.message.reply_text(f"✅ اشتراک کاربر @{username} برای ۳۰ روز تمدید شد.")
    try:
        bot.send_message(chat_id=user["chat_id"], text="🎉 اشتراک شما برای ۳۰ روز تمدید شد. ممنون از اعتماد شما!")
    except:
        pass

# =====================
# راهنما و آخرین سیگنال‌ها
# =====================
def guide(update: Update, context: CallbackContext):
    update.message.reply_text("📘 راهنمای ربات:\n\n1. با /start ثبت‌نام کن\n2. ۳ روز اشتراک رایگان داری\n3. برای تمدید اشتراک، با ما تماس بگیر")

def latest(update: Update, context: CallbackContext):
    if not os.path.exists(SIGNALS_FILE):
        update.message.reply_text("هنوز سیگنالی ثبت نشده.")
        return

    with open(SIGNALS_FILE, "r") as f:
        try:
            signals = json.load(f)[-3:]
        except:
            update.message.reply_text("خطا در خواندن سیگنال‌ها!")
            return

    msg = "📈 آخرین سیگنال‌ها:\n"
    for s in signals:
        msg += f"- {s.get('action', '').upper()} | {s.get('symbol')} | {s.get('price')}\n"

    update.message.reply_text(msg.strip())

# =====================
# اجرای ربات
# =====================
def run_bot():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("guide", guide))
    dp.add_handler(CommandHandler("latest", latest))
    dp.add_handler(CommandHandler("extend", extend))  # فقط برای ادمین

    updater.start_polling()
    print("🤖 ربات در حال اجراست...")
