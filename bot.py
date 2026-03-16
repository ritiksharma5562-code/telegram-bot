import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

TOKEN = "8687497631:AAE4niCmKtkhPsAy44zn04-bZOjJYg94Kd4"
ADMIN_ID = 5888788582

bot = telebot.TeleBot(TOKEN)

premium_channel = "https://t.me/+Pjf9kjog2Y81Njg1"
demo_channel = "https://t.me/+Pjf9kjog2Y81Njg1"
how_channel = " "

waiting_for_payment = {}
waiting_qr = False

# USERS LOAD
try:
    with open("users.txt","r") as f:
        users = set(f.read().splitlines())
except:
    users = set()

def save_user(user_id):
    user_id = str(user_id)

    if user_id not in users:
        users.add(user_id)

        with open("users.txt","a") as f:
            f.write(user_id+"\n")


start_text = """
𝐕𝐢𝐝𝐞𝐨 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 🌸

𝐅𝐨𝐫 𝐃𝐞𝐬𝐢 𝐂𝐨𝐧𝐭𝐞𝐧𝐭 𝐋𝐨𝐯𝐞𝐫𝐬 😋

𝐍𝐨 𝐒𝐧#𝐩, 𝐏𝐮𝐫𝐞 𝐃𝐞𝐬𝐢 𝐂𝐨𝐧𝐭𝐞𝐧𝐭 😙

𝐫𝐚𝐫𝐞 𝐃𝐞𝐬𝐢 𝐥𝐞#𝐤𝐬 𝐞𝐯𝐞𝐫.... 🎀

𝐉𝐮𝐬𝐭 𝐩𝐚𝐲 𝐚𝐧𝐝 𝐠𝐞𝐭 𝐞𝐧𝐭𝐫𝐲...

𝐍𝐨 - 𝐀𝐝𝐬 𝐒𝐡#𝐭 🔥

𝐏𝐫𝐢𝐜𝐞 :- ₹𝟗𝟗.𝟎𝟎/-

𝐕𝐚𝐥𝐢𝐝𝐢𝐭𝐲 :- 𝐥𝐢𝐟𝐞𝐭𝐢𝐦𝐞
"""

payment_text = """
1️⃣ Scan QR & Pay ₹99

2️⃣ Click on 'I HAVE PAID' button below 👇
"""

# START
@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id
    save_user(user_id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💎 Get Premium",callback_data="buy"))
    markup.add(InlineKeyboardButton("🎬 Premium Demo",url=demo_channel))
    markup.add(InlineKeyboardButton("📖 How To Get Premium",url=how_channel))

    photo = open("start.jpg","rb")

    bot.send_photo(message.chat.id,photo,caption=start_text,reply_markup=markup)


# USERS
@bot.message_handler(commands=['users'])
def users_count(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.reply_to(message,f"👥 Total Users: {len(users)}")


# BROADCAST
@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/broadcast ","")

    for user in users.copy():

        try:
            bot.send_message(int(user),text)
        except:
            pass

    bot.reply_to(message,"✅ Broadcast Sent")


# CHANNEL CHANGE COMMANDS
@bot.message_handler(commands=['setdemo'])
def set_demo(message):

    global demo_channel

    if message.from_user.id != ADMIN_ID:
        return

    demo_channel = message.text.split(" ")[1]

    bot.reply_to(message,"✅ Demo channel updated")


@bot.message_handler(commands=['sethow'])
def set_how(message):

    global how_channel

    if message.from_user.id != ADMIN_ID:
        return

    how_channel = message.text.split(" ")[1]

    bot.reply_to(message,"✅ How channel updated")


@bot.message_handler(commands=['setpremium'])
def set_premium(message):

    global premium_channel

    if message.from_user.id != ADMIN_ID:
        return

    premium_channel = message.text.split(" ")[1]

    bot.reply_to(message,"✅ Premium channel updated")


# SET QR
@bot.message_handler(commands=['setqr'])
def set_qr(message):

    global waiting_qr

    if message.from_user.id != ADMIN_ID:
        return

    waiting_qr = True

    bot.reply_to(message,"📷 Send new QR image")


@bot.message_handler(content_types=['photo'])
def update_qr(message):

    global waiting_qr

    if waiting_qr and message.from_user.id == ADMIN_ID:

        file_info = bot.get_file(message.photo[-1].file_id)

        downloaded = bot.download_file(file_info.file_path)

        with open("qr.jpg","wb") as new_file:
            new_file.write(downloaded)

        waiting_qr = False

        bot.reply_to(message,"✅ QR updated successfully")

        return


# BUTTON HANDLER
@bot.callback_query_handler(func=lambda call: True)
def buttons(call):

    user_id = call.from_user.id


    if call.data == "buy":

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ I HAVE PAID",callback_data="paid"))
        markup.add(InlineKeyboardButton("❌ Cancel",callback_data="back"))

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


    elif call.data == "paid":

        waiting_for_payment[user_id] = True

        bot.send_message(
            call.message.chat.id,
            "📸 Please send your payment screenshot now."
        )

        bot.answer_callback_query(call.id)


    elif call.data == "back":

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


# SCREENSHOT RECEIVE
@bot.message_handler(content_types=['photo'], func=lambda m: m.from_user.id in waiting_for_payment)
def payment_screenshot(message):

    uid = message.from_user.id

    if uid in waiting_for_payment and waiting_for_payment[uid]:

        markup = InlineKeyboardMarkup()

        markup.add(
            InlineKeyboardButton("✅ Approve",callback_data="approve_"+str(uid)),
            InlineKeyboardButton("❌ Reject",callback_data="reject_"+str(uid))
        )

        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=f"Payment Screenshot\n\nUser: @{message.from_user.username}\nID: {uid}",
            reply_markup=markup
        )

        bot.reply_to(message,"⏳ Screenshot sent for verification")

    else:

        bot.reply_to(message,"⚠️ This is not correct selection")


print("Bot Running...")
bot.infinity_polling(skip_pending=True)
