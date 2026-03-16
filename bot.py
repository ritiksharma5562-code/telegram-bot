import telebot
import json
import pytesseract
import cv2
import numpy as np
from PIL import Image
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 5888788582

bot = telebot.TeleBot(TOKEN)

premium_channel = "https://t.me/+aX_BhutfN11kNWQ1"
demo_channel = "https://t.me/+UATy4AN0lbo2NDg1"
how_channel = "https://t.me/AKASH_OP_001?text=hello+Sir+how+to+get+premium"

waiting_screenshot = {}
waiting_qr = False

# DATABASE
DB_FILE = "database.json"

def load_db():
    try:
        with open(DB_FILE,"r") as f:
            return json.load(f)
    except:
        return {"users":[]}

def save_db(data):
    with open(DB_FILE,"w") as f:
        json.dump(data,f)

db = load_db()
users = set(db["users"])

def save_user(uid):
    if uid not in users:
        users.add(uid)
        db["users"] = list(users)
        save_db(db)

# PAYMENT KEYWORDS
payment_keywords = [
"upi","transaction","paid","success","paytm","phonepe",
"google","gpay","debited","credited","₹"
]

def detect_payment(image_path):

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    text = pytesseract.image_to_string(gray).lower()

    for word in payment_keywords:
        if word in text:
            return True

    return False

# START
@bot.message_handler(commands=['start'])
def start(message):

    save_user(message.from_user.id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💎 Get Premium",callback_data="buy"))
    markup.add(InlineKeyboardButton("🎬 Premium Demo",url=demo_channel))
    markup.add(InlineKeyboardButton("📖 How To Get Premium",url=how_channel))

    bot.send_photo(
        message.chat.id,
        open("start.jpg","rb"),
        caption="Premium Access",
        reply_markup=markup
    )

# BUTTONS
@bot.callback_query_handler(func=lambda call: True)
def buttons(call):

    uid = call.from_user.id

    if call.data == "buy":

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("I HAVE PAID",callback_data="paid"))
        markup.add(InlineKeyboardButton("Cancel",callback_data="back"))

        media = InputMediaPhoto(
            open("qr.jpg","rb"),
            caption="Scan QR and pay ₹99"
        )

        bot.edit_message_media(
            media,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    elif call.data == "paid":

        waiting_screenshot[uid] = True

        bot.send_message(uid,"Send payment screenshot")

    elif call.data.startswith("approve_"):

        uid = int(call.data.split("_")[1])

        bot.send_message(
            uid,
            "Payment Approved\nJoin:\n"+premium_channel
        )

        bot.answer_callback_query(call.id,"Approved",show_alert=True)

    elif call.data.startswith("reject_"):

        uid = int(call.data.split("_")[1])

        bot.send_message(uid,"Payment Rejected")

        bot.answer_callback_query(call.id,"Rejected",show_alert=True)

# SCREENSHOT
@bot.message_handler(content_types=['photo'])
def screenshot(message):

    uid = message.from_user.id

    if uid not in waiting_screenshot:

        bot.reply_to(
            message,
            "⚠️𝐓𝐇𝐈𝐒 𝐈𝐒 𝐍𝐎𝐓 𝐂𝐎𝐑𝐑𝐄𝐂𝐓 𝐒𝐄𝐋𝐄𝐂𝐓𝐈𝐎𝐍 🥲\n𝐏𝐋𝐄𝐀𝐒𝐄, 𝐒𝐄𝐋𝐄𝐂𝐓 𝐅𝐑𝐎𝐌 𝐎𝐏𝐓𝐈𝐎𝐍𝐒✅"
        )
        return

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded = bot.download_file(file_info.file_path)

    with open("payment.jpg","wb") as f:
        f.write(downloaded)

    # AI CHECK
    if not detect_payment("payment.jpg"):

        bot.reply_to(
            message,
            "❌ Invalid payment screenshot\nSend correct payment proof"
        )

        return

    waiting_screenshot.pop(uid)

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Approve",callback_data="approve_"+str(uid)),
        InlineKeyboardButton("Reject",callback_data="reject_"+str(uid))
    )

    bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=f"Payment Screenshot\nUser: {uid}",
        reply_markup=markup
    )

    bot.reply_to(message,"Screenshot sent to admin")

print("Bot Running...")
bot.infinity_polling(skip_pending=True)
