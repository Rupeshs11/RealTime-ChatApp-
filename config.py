import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/knox_chat')
SECRET_KEY = os.environ.get('SECRET_KEY', 'knox-chat-secret-key-change-me')
DB_NAME = 'knox_chat'
