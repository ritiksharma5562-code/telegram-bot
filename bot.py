import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

TOKEN = "8687497631:AAE4niCmKtkhPsAy44zn04-bZOjJYg94Kd4"
ADMIN_ID = 5888788582

bot = telebot.TeleBot(TOKEN)

premium_channel = "https://t.me/+Pjf9kjog2Y81Njg1"
demo_channel = "https://t.me/+Pjf9kjog2Y81Njg1"
how_channel = "https://t.me/+Pjf9kjog2Y81Njg1"

waiting_for_payment = {}
users = set()
used_utr = set()

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

After payment send your 12 digit UTR number.
"""


# START
@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id
    users.add(user_id)

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


# ADMIN USERS COUNT
@bot.message_handler(commands=['users'])
def users_count(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.reply_to(message,f"👥 Total Users: {len(users)}")


# ADMIN BROADCAST
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

        bot.edit_message_text(
            f"✅ Payment Approved\n\nUser: {uid}",
            call.message.chat.id,
            call.message.message_id
        )

        bot.answer_callback_query(call.id,"✅ Approved Successfully")


    elif call.data.startswith("reject_"):

        uid = int(call.data.split("_")[1])

        bot.send_message(uid,"❌ Payment Rejected")

        bot.edit_message_text(
            f"❌ Payment Rejected\n\nUser: {uid}",
            call.message.chat.id,
            call.message.message_id
        )

        bot.answer_callback_query(call.id,"❌ Rejected Successfully")


# UTR CHECK
@bot.message_handler(func=lambda message: True)
def payment_check(message):

    uid = message.from_user.id
    text = message.text.strip()

    if text.startswith("/"):
        return

    if uid in waiting_for_payment and waiting_for_payment[uid]:

        if not text.isdigit() or len(text) != 12:

            bot.reply_to(message,"❌ Invalid UTR\n\nPlease send correct 12 digit UTR number.")
            return

        if text in used_utr:

            bot.reply_to(message,"⚠️ This UTR already used")
            return

        used_utr.add(text)

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Approve",callback_data="approve_"+str(uid)),
            InlineKeyboardButton("❌ Reject",callback_data="reject_"+str(uid))
        )

        bot.send_message(
            ADMIN_ID,
            f"Payment request\n\nUser: {uid}\nUTR: {text}",
            reply_markup=markup
        )

        bot.reply_to(message,"⏳ Payment sent for verification")

    else:

        bot.reply_to(message,"⚠️ This is not correct selection")


print("Bot Running...")
bot.infinity_polling(skip_pending=True)
