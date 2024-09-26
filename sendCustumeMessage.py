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

users = database.getAll()
message = input("enter your message:")

for user in users:
    bot.send_message(user["telid"],message.encode("utf-8"))