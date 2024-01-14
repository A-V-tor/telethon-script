import os
from dotenv import load_dotenv


load_dotenv()


class DevelopmentConfig:
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = True
