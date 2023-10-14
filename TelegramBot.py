import io
from api import *
import enviroment
import telebot

bot = telebot.TeleBot(enviroment.tellApiKey, parse_mode=None)

sfa = ShahedFoodApi()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = telebot.types.KeyboardButton("ورود")
    markup.add(item)
    bot.reply_to(message, "Welcome to Shahed Food Automation(SFA) :)")
	



# Sign-in command
@bot.message_handler(func=lambda message: message.text == 'ورود')
def signin(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "نام کاربری را وارد کنید")
    username = None
    password = None
    mode = "username"
    login_data = None

    @bot.message_handler(func=lambda msg: msg.chat.id == message.chat.id and mode == "username")
    def get_username(msg):
        nonlocal username, mode
        username = msg.text
        bot.send_message(message.chat.id, "رمز عبور خود را وارد کنید")
        mode = "password"

    @bot.message_handler(func=lambda msg: msg.chat.id == message.chat.id and mode =="password")
    def get_password(msg):
        nonlocal password, mode, login_data
        mode = "captcha"
        password = msg.text
        print(f"Username: {username}")
        print(f"Password: {password}")
        (login_data, capcha_binary) = sfa.loginBeforeCaptcha()
        bot.send_photo(user_id,photo=io.BytesIO(capcha_binary))


    @bot.message_handler(func=lambda msg: msg.chat.id == message.chat.id and mode =="captcha")
    def get_password(msg):
        nonlocal password, mode, login_data
        mode = "username"
        captcha_code = msg.text
        sfa.loginAfterCaptcha(
        login_data,
        username, password,
        captcha_code)
        bot.send_message(message.chat.id, sfa.getCredit())


@bot.message_handler(func=lambda message: message.text == 'لیست غذا')
def getFood(message):
    user_id = message.from_user.id
    if not sfa.signedIn:
        bot.send_message(user_id, "اول وارد شوید")
        return False
    listOfFood = sfa.getFood()
    result = ""
    for food in listOfFood:
        result = result +  f"\n{str(food['DayName'])}  {str(food['Date'])} \n {str(food['FoodName'])} \t {str(food['Price'])}\n"
    bot.send_message(user_id, result)




# # Custom command
# @bot.message_handler(func=lambda message: message.text.startswith('/customcommand'))
# def custom_command(message):
#     user_id = message.from_user.id
#     user_username = message.from_user.username
#     users_collection = ""
#     # Check if the user is signed in based on MongoDB data
#     user_document = users_collection.find_one({"_id": user_username})
#     if user_document and user_document.get("signed_in"):
#         # Handle your custom command logic here
#         response = f"Command received: {message.text}"
#         bot.send_message(user_id, response)
#     else:
#         bot.send_message(user_id, "Please sign in first using /signin.")


# # Cancel command
# @bot.message_handler(commands=['cancel'])
# def cancel(message):
#     user_id = message.from_user.id


# @bot.message_handler(commands=['getReport'])
# def get_report_bot(message):
#     user_id = message.from_user.id
#     bot.send_message(user_id, "آدرس سایت را وارد کنید")
#     bot.register_next_step_handler(message, process_input)


# def process_input(message):
#     user_id = message.from_user.id
#     site = Site(message.text)
#     logic.get_report(site)
#     try:
#         with open("files.pdf", 'rb') as pdf_file:
#             bot.send_document(user_id, pdf_file)
#     except Exception as e:
#         bot.send_message(user_id, f"Error: {str(e)}")

#     bot.send_message(user_id, "Done.")

# def get_report(site,user_id):
#     site = Site(site)
#     logic.get_report(site)
#     try:
#         with open("files.pdf", 'rb') as pdf_file:
#             bot.send_document(user_id, pdf_file)
#     except Exception as e:
#         bot.send_message(user_id, f"Error: {str(e)}")
#     if os.path.exists("files.pdf"):
#         os.remove("files.pdf")


# @bot.message_handler(func=lambda message: message.text == 'فهرست')
# def menu(message):
#     keyboard = telebot.types.InlineKeyboardMarkup()
#     keyboard.add(telebot.types.InlineKeyboardButton('لیست سایت ها', callback_data='sites'))
#     keyboard.add(telebot.types.InlineKeyboardButton('سایت SEO GPT', url="https://www.seogptir.ir"))
#     keyboard.add(telebot.types.InlineKeyboardButton('پشتیبانی', url="mailto:info@seogptir.ir"))
#     keyboard.add(telebot.types.InlineKeyboardButton('خبرنامه', url="https://www.seogptir.ir"))
#     bot.send_message(message.chat.id, 'بخش مورد نظر خود را انتخاب کنید', reply_markup=keyboard)


# @bot.callback_query_handler(func=lambda c: True)
# def submenus(c):
#     if c.data == 'sites':
#         user_db = mongoDB(db="seogpt")
#         res = user_db.connect()
#         print(c.from_user.id)
#         user_document = user_db.find_all({"telBot_id": c.from_user.id}, "users")
#         print(type(user_document))
#         keyboard = telebot.types.InlineKeyboardMarkup()
#         for user in user_document:
#             print("test2")
#             for site in sorted(user["list of sites"]):
#                 callback = f"{site[8:]}" if site.find("https") != -1 else f"{site[7:]}---"
#                 print(callback)
#                 keyboard.add(telebot.types.InlineKeyboardButton(f"{site}", callback_data=f"{callback}"))
#         bot.send_message(c.message.chat.id, '''لیست سایت ها\n برای گرفتن آخرین گزارش، سایت مورد نظر را انتخاب کنید.''', reply_markup=keyboard)
#         user_db.disconnect()
#     elif c.data != "sites":
#         if c.data[-3:] == '---':
#             c.data = 'http://' + c.data[:-3]
#             print(c.data)
#         else:
#             c.data = 'https://' + c.data
#             print(c.data)
#         get_report(c.data, c.from_user.id)
bot.infinity_polling()