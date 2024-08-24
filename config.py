import os
from dotenv import load_dotenv

load_dotenv()

BASIC_AUTH_USERNAME = os.getenv('BASIC_AUTH_USERNAME', 'default_user')
BASIC_AUTH_PASSWORD = os.getenv('BASIC_AUTH_PASSWORD', 'default_password')