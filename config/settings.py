import os

from dotenv import load_dotenv


load_dotenv()


FILEFORGE_DATABASE_URL = os.getenv(
    "FILEFORGE_DATABASE_URL"
)