import os
from pathlib import Path

from dotenv import load_dotenv

env_file = os.environ.get("ENV_FILE", "")
if env_file:
    load_dotenv(env_file)


SQL_USR = os.environ["SQL_USR"]
SQL_PSWRD = os.environ["SQL_PSWRD"]
SQL_HOST = os.environ["SQL_HOST"]
SQL_PORT = os.environ["SQL_PORT"]
SQL_DB = os.environ["SQL_DB"]