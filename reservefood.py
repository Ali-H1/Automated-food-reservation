from pysondb import db
import requests
import json
from src.api import *
from TelegramBot import decrypt_password, encrypt_password
# Initialize the database
database = db.getDb("./db/users.json")  # Replace with your actual database file

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
    food_list = sfa.getFood()
    for day in user["days"]:
        for food in food_list:
            if food["DayName"] == day:
                result = sfa.reserveFood(food)
                print(json.loads(result)[0]["StateCode"], json.loads(result)[0]["StateMessage"])

all_users = database.getAll()
    
# Check each user
for user in all_users:
    reserve_food(user)