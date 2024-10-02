import io
from src.api import *
import environmets
import telebot
from telebot.types import BotCommand
from pysondb import db
import json
import requests
import ast
from cryptography.fernet import Fernet
import platform

db_path = './db/users.json' if platform.system() == 'Windows' else f'{environmets.dbPath}/users.json'
database = db.getDb(db_path)  # Replace with your actual database file

bot = telebot.TeleBot(environmets.tellApiKey, parse_mode=None)

key_path = 'secret.key' if platform.system() == 'Windows' else f'{environmets.keyPath}/secret.key'
def load_key():
    return open(key_path, "rb").read()


# Function to encrypt a password
def encrypt_password(password):
    key = load_key()
    f = Fernet(key)
    encrypted_password = f.encrypt(password.encode())
    return encrypted_password

# Function to decrypt an encrypted password
def decrypt_password(encrypted_password):
    key = load_key()
    f = Fernet(key)
    decrypted_password = f.decrypt(encrypted_password.encode('utf-8')).decode()
    return decrypted_password

def store_session(session, id):
    # Convert session cookies and headers to JSON serializable format
    session_data = {
        "cookies": dict(requests.utils.dict_from_cookiejar(session.cookies)),
        "headers": dict(session.headers)
    }
    
    # Save session to pysonDB
    database.updateById(id,{"session": json.dumps(session_data)})

def restore_session(id, key="session"):
    # Fetch session data from pysonDB
    session_data = database.getById(id)
    if not session_data:
        raise ValueError("Session data not found")
    
    # Load session data
    session_data = json.loads(session_data[key])
    
    # Restore session
    session = requests.Session()
    session.cookies = requests.utils.cookiejar_from_dict(session_data["cookies"])
    session.headers.update(session_data["headers"])
    
    return session

def is_session_valid(session):
    """Checks if the current session is still valid by accessing a protected page."""
    response = session.get(f"{apiv0}/credit")
    if response.status_code == 200 and "<html" not in response.content.decode('utf8').replace("'", '"'):
        return True
    else:
        return False

def get_valid_session(sfa,id):
    """Restores the session if valid, otherwise logs in and stores a new session."""
    try:
        # Try restoring the session
        session = restore_session(id)
        if is_session_valid(session):
            print("Session is valid.")
            return session
        else:
            print("Session is invalid. Logging in again.")
    except ValueError:
        print("No stored session found. Logging in again.")
    user = database.getById(id)
    username = user["username"]
    password = decrypt_password(user["password"])
    (login_data, capcha_binary) = sfa.login_before_captcha()
    sfa.login_after_captcha(
    login_data,
    username, password,
    0)

    return sfa.currentSession


def set_bot_commands():
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("signin", "log into your account"),
        # BotCommand("Autoreserve", "ff")
        BotCommand("FoodList", "list of meals")
        # BotCommand("DaysOfWeek", "days of week with auto reserve")
    ]
    bot.set_my_commands(commands)

###################################################################
markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
item = telebot.types.KeyboardButton("🔓 ورود")
markup.add(item)
item2 = telebot.types.KeyboardButton("📆 روزهای هفته")
# markup.add(item2)
item3 = telebot.types.KeyboardButton("🍽 لیست غذا")
# markup.add(item3)
item4 = telebot.types.KeyboardButton("🍽📆 لیست غذای هفته بعد")
# markup.add(item4)
item5 = telebot.types.KeyboardButton("🤖 رزرو خودکار")
# markup.add(item5)
markup.row(item4,item3)
markup.row(item2,item5)
item6 = telebot.types.KeyboardButton("⏲ رزرو آنی غذا")
item7 = telebot.types.KeyboardButton('⏲  رزرو آنی غذا هفته بعد')
markup.row(item6,item7)


##############################################################
def reserve_food(user, week):
    sfa = ShahedFoodApi()
    sfa.currentSession = get_valid_session(sfa, user["id"])
    food_list = sfa.getFood(week)
    if not food_list:
        bot.send_message(user["telid"], f"برنامه غذایی هنوز اعلام نشده است")
        return
    reserved = []
    for day in user["days"]:
        for food in food_list:
            if food["DayName"] == day:
                result = sfa.reserveFood(food)
                if json.loads(result)[0]["StateCode"] in [0,2]:
                    reserved.append(day)
                print(json.loads(result)[0]["StateCode"])#, json.loads(result)[0]["StateMessage"])
    if reserved:
        bot.send_message(user["telid"], f"غذا برای روز های {reserved} رزرو شده است")
    else:
        bot.send_message(user["telid"], f"غذا برای هیچ روزی رزرو نشد!\n{json.loads(result)[0]['StateMessage']}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # markup = telebot.types.ReplyKeyboardMarkup()
    bot.reply_to(message, """راهنمای استفاده از ربات رزرو غذای دانشگاه شاهد

مرحله 1: ورود به سیستم
1. وارد کردن نام کاربری و رمز عبور
   - ابتدا پس از باز کردن ربات، نام کاربری و رمز عبور خود را وارد کنید.
   - بر روی دکمه "ورود" کلیک کنید تا وارد حساب کاربری خود شوید.

 مرحله 2: مشاهده امکانات
پس از ورود موفقیت‌آمیز، با چهار گزینه زیر مواجه خواهید شد:

1. لیست غذای هفته بعد 🍽
   - با کلیک بر روی این گزینه می‌توانید لیست غذاهای ارائه شده برای هفته آینده را مشاهده کنید.

2. لیست غذا 🍱
   - این گزینه لیستی از غذاهای موجود برای هفته جاری را نشان می‌دهد تا بتوانید انتخاب نمایید.

3. روزهای هفته 📅
   - در این بخش می‌توانید روزهایی که قصد رزرو غذا دارید را مشخص کرده و تنظیمات مربوط به رزرو اتوماتیک انجام دهید.

4. رزرو خودکار 🤖
   - با انتخاب این گزینه، ربات به صورت اتوماتیک براساس تنظیمات شما (که در بخش "روزهای هفته" انجام داده‌اید) اقدام به رزرو غذا خواهد کرد.
   
5. رزرو آنی غذا 🍲
    - اگر تمایل دارید بلافاصله برنامه غذایی خود را برای هفته بعد رزرو کنید، میتوانید از طریق این دکمه اقدام نمایید.

 توضیحات تکمیلی:
- پس از انتخاب هر یک از گزینه‌های بالا، دستورات مربوطه نمایش داده خواهند شد که باید طبق آن‌ها عمل کنید.

امیدواریم تجربه‌ی خوبی داشته باشید!
Alihdad""", reply_markup=markup)
	


# Sign-in command
@bot.message_handler(func=lambda message: message.text == '🔓 ورود')
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
        valid = True
        for i in username:
            if i not in "0123456789":
                bot.send_message(message.chat.id, "نام کابری معتبر نیست(فقط حروف انگلیسی)")
                mode = "username"
                valid = False
                break
        if valid:
            bot.send_message(message.chat.id, "رمز عبور خود را وارد کنید")
            mode = "password"

    @bot.message_handler(func=lambda msg: msg.chat.id == message.chat.id and mode =="password")
    def get_password(msg):
        nonlocal password, mode, login_data
        mode = "other"
        password = msg.text
        bot.send_message(message.chat.id, "چند لحظه صبر کنید...")
        print(f"Username: {username}")
        print(f"Password: {encrypt_password(password)}")
        user = database.getByQuery({"username":username})
        if not len(user):
            sfa = ShahedFoodApi()
            (login_data, capcha_binary) = sfa.login_before_captcha()
            sfa.login_after_captcha(
            login_data,
            username, password,
            0)
            if sfa.signedIn:
                name = ""
                if message.from_user.first_name:
                    if message.from_user.last_name:
                        name += message.from_user.first_name + message.from_user.last_name
                    else:
                        name += message.from_user.first_name
                user_db_id = database.add({"username":username, "password":encrypt_password(password).decode('utf8').replace("'", '"'), "telid":user_id, "chatid":message.chat.id,"name":name,"tel_username":message.from_user.username, "autoReserve":False, "session":0, "days":[]})
                store_session(sfa.currentSession, user_db_id)
                bot.send_message(message.chat.id, "شما وارد شدید")
                if markup.keyboard[0][0]["text"] == "🔓 ورود":
                    markup.keyboard[0].pop(0)
                bot.send_message(message.chat.id, "راهنمای بات: \n- 🍽 لیست غذا\n- 📆 روزهای هفته\n- 🤖 رزرو خودکار", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "نام کاربری یا رمز عبور نادرست است")
                signin(message)
        elif user[0]["telid"] == user_id:
            sfa = ShahedFoodApi()
            (login_data, capcha_binary) = sfa.login_before_captcha()
            sfa.login_after_captcha(
            login_data,
            username, password,
            0)
            if sfa.signedIn:
                store_session(sfa.currentSession, user[0]["id"])
                bot.send_message(message.chat.id, "شما وارد شدید")
                if markup.keyboard[0][0]["text"] == "🔓 ورود":
                    markup.keyboard[0].pop(0)
                bot.send_message(message.chat.id, "راهنمای بات: \n- 🍽 لیست غذا\n- 📆 روزهای هفته\n- 🤖 رزرو خودکار", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "نام کاربری یا رمز عبور نادرست است", reply_markup=markup)
                signin(message)
        else:
            bot.send_message(message.chat.id, "دستگاه دیگری قبلا با این حساب وارد شده است", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🍽 لیست غذا')
def getFood(message):
    user_id = message.from_user.id
    user = database.getByQuery({"telid":user_id})
    if not user:
        signin(message)
        user = database.getByQuery({"telid":user_id})
    sfa = ShahedFoodApi()
    sfa.currentSession = get_valid_session(sfa, user[0]["id"])
    listOfFood = sfa.getFood()
    result = ""
    if not listOfFood:
        bot.reply_to(message, f"برنامه غذایی هنوز اعلام نشده است")
        return
    if listOfFood == "error":
        bot.reply_to(message, f"مشکلی پیش آمده است")
        return
    for food in listOfFood:
        result = result +  f"\n🔵{str(food['DayName'])}  {str(food['Date'])} \n - {str(food['FoodName'])} \t 💵{str(food['Price'])}\n"
    bot.reply_to(message, result+"\n@ShahedFAbot\n")

@bot.message_handler(func=lambda message: message.text == '🍽📆 لیست غذای هفته بعد')
def getFood(message):
    user_id = message.from_user.id
    user = database.getByQuery({"telid":user_id})
    if not user:
        signin(message)
        user = database.getByQuery({"telid":user_id})
    sfa = ShahedFoodApi()
    sfa.currentSession = get_valid_session(sfa, user[0]["id"])
    listOfFood = sfa.getFood(1)
    result = ""
    if not listOfFood:
        bot.reply_to(message, f"برنامه غذایی هنوز اعلام نشده است")
        return
    if listOfFood == "error":
        bot.reply_to(message, f"مشکلی پیش آمده است")
        return
    for food in listOfFood:
        result = result +  f"\n🔵{str(food['DayName'])}  {str(food['Date'])} \n - {str(food['FoodName'])} \t 💵{str(food['Price'])}\n"
    bot.reply_to(message, result+"\n@ShahedFAbot\n")

@bot.message_handler(func=lambda message: message.text == '⏲ رزرو آنی غذا')
def getFood(message):
    user_id = message.from_user.id
    user = database.getByQuery({"telid":user_id})
    if not user:
        signin(message)
        user = database.getByQuery({"telid":user_id})
    reserve_food(user[0],0)

@bot.message_handler(func=lambda message: message.text == '⏲  رزرو آنی غذا هفته بعد')
def getFood(message):
    user_id = message.from_user.id
    user = database.getByQuery({"telid":user_id})
    if not user:
        signin(message)
        user = database.getByQuery({"telid":user_id})
    reserve_food(user[0],1)


@bot.message_handler(func=lambda message: message.text == '📆 روزهای هفته')
def setdays(message):
    user_id = message.from_user.id
    user = database.getByQuery({"telid":user_id})
    if not user:
        signin(message)
        user = database.getByQuery({"telid":user_id})
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton('شنبه', callback_data=str(['0', message.chat.id])))
    keyboard.add(telebot.types.InlineKeyboardButton('یکشنبه', callback_data=str(['1',message.chat.id])))
    keyboard.add(telebot.types.InlineKeyboardButton('دوشنبه', callback_data=str(['2',message.chat.id])))
    keyboard.add(telebot.types.InlineKeyboardButton('سه شنبه', callback_data=str(['3',message.chat.id])))
    keyboard.add(telebot.types.InlineKeyboardButton('چهار شنبه', callback_data=str(['4',message.chat.id])))
    bot.send_message(message.chat.id, f'روز های که میخواهید رزرو کنید را مشخص کنید\n روز های فعال:{user[0]["days"]}', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '🤖 رزرو خودکار')
def setdays(message):
    user_id = message.from_user.id
    user = database.getByQuery({"telid":user_id})
    if not user:
        signin(message)
        user = database.getByQuery({"telid":user_id})
    status = "فعال " if user[0]["autoReserve"] else "غیرفعال"
    keyboard = telebot.types.InlineKeyboardMarkup()
    if status== "فعال ":
        keyboard.add(telebot.types.InlineKeyboardButton('غیر فعال سازی', callback_data=str(['disable', message.chat.id])))
    elif status== "غیرفعال":
        keyboard.add(telebot.types.InlineKeyboardButton('فعال سازی', callback_data=str(['enable', message.chat.id])))
    bot.send_message(message.chat.id, f'رزرو خودکار برای شما "{status}" است', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: True)
def submenus(c):
    c.data = ast.literal_eval(c.data)
    user_id = c.from_user.id
    user = database.getByQuery({"telid":user_id})[0]
    if c.data[0] == '0':
        if "شنبه" not in user["days"]:
            user["days"].append("شنبه")
            database.updateById(user["id"],{"days":user["days"]})
        else:
            user["days"].remove("شنبه")
            database.updateById(user["id"],{"days":user["days"]})
        bot.send_message(str(c.data[1]), f' روز های فعال:{user["days"]}', reply_markup=markup)

    elif c.data[0] == "1":
        if "یکشنبه" not in user["days"]:
            user["days"].append("یکشنبه")
            database.updateById(user["id"],{"days":user["days"]})
        else:
            user["days"].remove("یکشنبه")
            database.updateById(user["id"],{"days":user["days"]})
        bot.send_message(str(c.data[1]), f' روز های فعال:{user["days"]}', reply_markup=markup)

    elif c.data[0] == '2':
        if "دوشنبه" not in user["days"]:
            user["days"].append("دوشنبه")
            database.updateById(user["id"],{"days":user["days"]})
        else:
            user["days"].remove("دوشنبه")
            database.updateById(user["id"],{"days":user["days"]})
        bot.send_message(str(c.data[1]), f' روز های فعال:{user["days"]}', reply_markup=markup)

    elif c.data[0] == '3':
        if "سه شنبه" not in user["days"]:
            user["days"].append("سه شنبه")
            database.updateById(user["id"],{"days":user["days"]})
        else:
            user["days"].remove("سه شنبه")
            database.updateById(user["id"],{"days":user["days"]})
        bot.send_message(str(c.data[1]), f' روز های فعال:{user["days"]}', reply_markup=markup)

    elif c.data[0] == '4':
        if "چهارشنبه" not in user["days"]:
            user["days"].append("چهارشنبه")
            database.updateById(user["id"],{"days":user["days"]})
        else:
            user["days"].remove("چهارشنبه")
            database.updateById(user["id"],{"days":user["days"]})
        bot.send_message(str(c.data[1]), f' روز های فعال:{user["days"]}', reply_markup=markup)

    elif c.data[0] == 'enable':
        database.updateById(user["id"],{"autoReserve":True})
        bot.send_message(str(c.data[1]), f' رزرو خودکار فعال شد')
        bot.send_message(str(c.data[1]), f' روز های فعال:{user["days"]}', reply_markup=markup)
    elif c.data[0] == 'disable':
        database.updateById(user["id"],{"autoReserve":False})
        bot.send_message(str(c.data[1]), f' رزرو خودکار غیرفعال شد', reply_markup=markup)

# set_bot_commands()

bot.infinity_polling()