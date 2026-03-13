import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    INFLUX_HOST = os.getenv("INFLUX_HOST")
    INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
    INFLUX_DATABASE = os.getenv("INFLUX_DATABASE")

settings = Settings()
