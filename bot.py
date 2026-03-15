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

USERS_FILE = "users.json"
UTR_FILE = "utr.json"

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


# START COMMAND
@bot.message_handler(commands=['start'])
def start(message):

    users.add(message.chat.id)
    save_users()

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💎 Get Premium", callback_data="buy"))
    markup.add(InlineKeyboardButton("🎬 Premium Demo", url=demo_channel))
    markup.add(InlineKeyboardButton("📖 How To Get Premium", url=how_channel))

    photo = open("start.jpg","rb")

    bot.send_photo(
        message.chat.id,
        photo,
        caption=start_text,
        reply_markup=markup
    )


# ADMIN COMMANDS
@bot.message_handler(commands=['users'])
def users_count(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.reply_to(message,f"👥 Total Users: {len(users)}")


@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/broadcast ","")

    for user in users:
        try:
            bot.send_message(user,text)
        except:
            pass

    bot.reply_to(message,"✅ Broadcast Sent")


# BUTTON HANDLER
@bot.callback_query_handler(func=lambda call: True)
def buttons(call):

    user_id = call.from_user.id

    if call.data == "buy":

        waiting_for_payment[user_id] = True

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅ Back",callback_data="back"))

        media = InputMediaPhoto(
            open("qr.jpg","rb"),
            caption=payment_text
        )

        bot.edit_message_media(
            media,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

        bot.answer_callback_query(call.id)

    elif call.data == "back":

        waiting_for_payment[user_id] = False

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💎 Get Premium",callback_data="buy"))
        markup.add(InlineKeyboardButton("🎬 Premium Demo",url=demo_channel))
        markup.add(InlineKeyboardButton("📖 How To Get Premium",url=how_channel))

        media = InputMediaPhoto(
            open("start.jpg","rb"),
            caption=start_text
        )

        bot.edit_message_media(
            media,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

        bot.answer_callback_query(call.id)

    elif call.data.startswith("approve_"):

        uid = int(call.data.split("_")[1])

        bot.send_message(
            uid,
            "✅ Payment Verified!\n\nJoin your private channel:\n"+premium_channel
        )

        bot.answer_callback_query(call.id,"✅ Approved")

    elif call.data.startswith("reject_"):

        uid = int(call.data.split("_")[1])

        bot.send_message(uid,"❌ Payment Rejected")

        bot.answer_callback_query(call.id,"❌ Rejected")


# UTR HANDLER
@bot.message_handler(func=lambda m: True)
def check_payment(message):

    uid = message.from_user.id

    if message.text.startswith("/"):
        return

    if uid in waiting_for_payment and waiting_for_payment[uid]:

        utr = message.text.strip()

        if utr in used_utr:
            bot.reply_to(message,"⚠️ This UTR already used")
            return

        used_utr.add(utr)
        save_utr()

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Approve",callback_data="approve_"+str(uid)),
            InlineKeyboardButton("❌ Reject",callback_data="reject_"+str(uid))
        )

        bot.send_message(
            ADMIN_ID,
            f"Payment request\n\nUser: {uid}\nUTR: {utr}",
            reply_markup=markup
        )

        bot.reply_to(message,"⏳ Payment Sent For Verification")

    else:

        bot.reply_to(message,"⚠️ This is not correct selection")


print("Bot Running...")
bot.infinity_polling()
