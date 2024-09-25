from pysondb import db
import requests
import json
from src.api import *
from cryptography.fernet import Fernet
import telebot
import environmets
import platform

bot = telebot.TeleBot(environmets.tellApiKey, parse_mode=None)

# Initialize the database
db_path = './db/users.json' if platform.system() == 'Windows' else f'{environmets.dbPath}/users.json'

database = db.getDb(db_path)  # Replace with your actual database file

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


def get_valid_session(sfa,id):
    """Restores the session if valid, otherwise logs in and stores a new session."""
    user = database.getById(id)
    username = user["username"]
    password = decrypt_password(user["password"])
    (login_data, capcha_binary) = sfa.login_before_captcha()
    sfa.login_after_captcha(
    login_data,
    username, password,
    0)

    return sfa.currentSession

# Function to get users with specific days
def get_users_with_days(specific_days):
    users_with_days = {}
    for day in specific_days:
        users_with_days[day] = []
    # Fetch all users from the database
    all_users = database.getAll()
    
    # Check each user
    for user in all_users:
        user_days = user["days"]
        # Check if any of the specific days are in the user's days
        for day in specific_days:
            if day in user_days:
                users_with_days[day].append(user["id"])
    
    return users_with_days

# Days you want to check for
days_to_check = ["شنبه", "یکشنبه", "دوشنبه", "سه شنبه", "چهارشنبه"]

# Get all users who have any of the specified days
users = get_users_with_days(days_to_check)

# Print the results
# print("Users with specified days:")
# print(users)

def reserve_food(user):
    sfa = ShahedFoodApi()
    sfa.currentSession = get_valid_session(sfa, user["id"])
    food_list = sfa.getFood(1)
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
        bot.send_message(user["telid"], f"غذا برای هیچ روزی رزرو نشد!")

all_users = database.getByQuery({"autoReserve":True})
    
# Check each user
for user in all_users:
    print(user["username"])
    reserve_food(user)