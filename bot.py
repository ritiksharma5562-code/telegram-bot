import telebot
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

TOKEN = "8687497631:AAHvd0LgeEiuw2knoRd5nGf31yG1ZQr7dA4"
ADMIN_ID = 5888788582

bot = telebot.TeleBot(TOKEN)

premium_channel = "https://t.me/+Pjf9kjog2Y81Njg1"
demo_channel = "https://t.me/+Pjf9kjog2Y81Njg1"
how_channel = "https://t.me/+Pjf9kjog2Y81Njg1"

waiting_for_payment = {}
waiting_qr = False

# FILES
USERS_FILE = "users.json"
UTR_FILE = "utr.json"

# LOAD DATABASE
try:
    with open(USERS_FILE) as f:
        users = set(json.load(f))
except:
    users = set()

try:
    with open(UTR_FILE) as f:
        used_utr = set(json.load(f))
except:
    used_utr = set()

def save_users():
    with open(USERS_FILE,"w") as f:
        json.dump(list(users),f)

def save_utr():
    with open(UTR_FILE,"w") as f:
        json.dump(list(used_utr),f)

start_text = """
Video Channel 🌸

For Desi Content Lovers 😋
No Sn#p, Pure Desi Content 😙
rare Desi le#ks ever.... 🎀

Just pay and get entry...

No - Ads Sh#t 🔥

Price :- ₹99.00/-
Validity :- lifetime
"""

payment_text = """
Make the payment of ₹99.00

After payment send your UTR number.
"""

# START
@bot.message_handler(commands=['start'])
def start(message):

    users.add(message.chat.id)
    save_users()

    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("💎 Get Premium", callback_data="buy"))
    markup.add(InlineKeyboardButton("🎬 Premium Demo", url=demo_channel))
    markup.add(InlineKeyboardButton("📖 How To Get Premium", url=how_channel))

    photo = open("/storage/emulated/0/Download/start.jpg","rb")

    bot.send_photo(message.chat.id, photo, caption=start_text, reply_markup=markup)


# BUTTON HANDLER
@bot.callback_query_handler(func=lambda call: True)
def buttons(call):

    user_id = call.from_user.id

    if call.data == "buy":

        waiting_for_payment[user_id] = True

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅ Back", callback_data="back"))

        media = InputMediaPhoto(
            open("/storage/emulated/0/Download/qr.jpg","rb"),
            caption=payment_text
        )

        bot.edit_message_media(
            media,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

    elif call.data == "back":

        waiting_for_payment[user_id] = False

        markup = InlineKeyboardMarkup()

        markup.add(InlineKeyboardButton("💎 Get Premium", callback_data="buy"))
        markup.add(InlineKeyboardButton("🎬 Premium Demo", url=demo_channel))
        markup.add(InlineKeyboardButton("📖 How To Get Premium", url=how_channel))

        media = InputMediaPhoto(
            open("/storage/emulated/0/Download/start.jpg","rb"),
            caption=start_text
        )

        bot.edit_message_media(
            media,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

    elif call.data.startswith("approve_"):

        data = call.data.split("_")
        user_id = int(data[1])
        utr = data[2]

        used_utr.add(utr)
        save_utr()

        bot.send_message(
            user_id,
            f"✅ Payment Verified\n\nHere is your private channel link 👇\n\n{premium_channel}"
        )

        bot.edit_message_text(
            f"✅ Payment Approved\n\nUser ID: {user_id}\nUTR: {utr}",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )

        bot.answer_callback_query(call.id,"Approved")

    elif call.data.startswith("reject_"):

        data = call.data.split("_")
        user_id = int(data[1])

        bot.send_message(user_id,"❌ Payment not found")

        bot.edit_message_text(
            f"❌ Payment Rejected\n\nUser ID: {user_id}",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )

        bot.answer_callback_query(call.id,"Rejected")


# MESSAGE HANDLER
@bot.message_handler(func=lambda message: True)
def verify(message):

    global waiting_qr, demo_channel, how_channel, premium_channel

    if message.from_user.id == ADMIN_ID:

        if message.text.startswith("/setdemo"):
            demo_channel = message.text.split(" ")[1]
            bot.reply_to(message,"Demo channel updated")
            return

        if message.text.startswith("/sethow"):
            how_channel = message.text.split(" ")[1]
            bot.reply_to(message,"How channel updated")
            return

        if message.text.startswith("/setpremium"):
            premium_channel = message.text.split(" ")[1]
            bot.reply_to(message,"Premium channel updated")
            return

        if message.text.startswith("/broadcast"):

            msg = message.text.replace("/broadcast ","")

            for user in users:
                try:
                    bot.send_message(user,msg)
                except:
                    pass

            bot.reply_to(message,"Broadcast sent")
            return

        if message.text == "/stats":

            bot.reply_to(
                message,
                f"""
Bot Statistics

Users: {len(users)}
Payments: {len(used_utr)}
"""
            )
            return

        if message.text == "/setqr":
            waiting_qr = True
            bot.reply_to(message,"Send new QR image")
            return

    if waiting_qr and message.photo:

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)

        with open("/storage/emulated/0/Download/qr.jpg","wb") as f:
            f.write(downloaded)

        waiting_qr = False
        bot.reply_to(message,"QR updated successfully")
        return

    user_id = message.from_user.id

    if not waiting_for_payment.get(user_id):

        bot.reply_to(message,"❌ This is not correct selection\n\nPlease click Get Premium first.")
        return

    utr = message.text.strip()

    if not utr.isdigit() or len(utr) != 12:

        bot.reply_to(message,"❌ Invalid UTR")
        return

    if utr in used_utr:

        bot.reply_to(message,"❌ This UTR already used")
        return

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton("✅ Approve",callback_data=f"approve_{message.chat.id}_{utr}"),
        InlineKeyboardButton("❌ Reject",callback_data=f"reject_{message.chat.id}")
    )

    bot.send_message(
        ADMIN_ID,
        f"New Payment Request\n\nUser ID: {message.chat.id}\nUTR: {utr}",
        reply_markup=markup
    )

    bot.reply_to(message,"⏳ Payment verification in progress...")


print("Bot Running...")
bot.infinity_polling()