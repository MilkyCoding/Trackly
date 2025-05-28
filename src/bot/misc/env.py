from os import environ
from typing import Final
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TgKeys:
    TOKEN: Final = environ.get('TOKEN')
    
    if not TOKEN:
        raise ValueError("No token provided. Please set TOKEN in .env file")
    
    if ' ' in TOKEN:
        raise ValueError("Token cannot contain spaces. Please check your .env file")
