from dotenv import load_dotenv
import os


load_dotenv()
BOT_TOKEN =os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ADMIN_STR= os.getenv("ADMIN_ID")
ADMINS = ADMIN_STR.split(',') if ADMIN_STR else []

