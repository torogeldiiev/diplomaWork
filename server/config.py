""""
Loads necessary environment variables making sure they are kept in secret, preventing data losses
"""
import os
import logging
from dotenv import load_dotenv

env_file = os.environ.get("ENV_FILE", "")
if env_file:
    load_dotenv(env_file)


SQL_USR = os.environ["SQL_USR"]
SQL_PSWRD = os.environ["SQL_PSWRD"]
SQL_HOST = os.environ["SQL_HOST"]
SQL_PORT = os.environ["SQL_PORT"]
SQL_DB = os.environ["SQL_DB"]

DATABASE_URL = f"postgresql+psycopg2://{SQL_USR}:{SQL_PSWRD}@{SQL_HOST}:{SQL_PORT}/{SQL_DB}"

JENKINS_USER = os.environ["JENKINS_USER"]
JENKINS_API_TOKEN = os.environ["JENKINS_API_TOKEN"]
JENKINS_PSWRD=os.environ["JENKINS_PSWRD"]
JENKINS_URL = os.environ["JENKINS_URL"]

JENKINS_PROJECT_NAMES = {
    "Configdiff": "cdpd-trigger-confdiff-test",
    "Platform": "cdpd-trigger-platform-tests"
}

log_level_str = os.environ["LOG_LEVEL"]
LOG_LEVEL = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}[log_level_str]

LOGGING_HANDLERS = [logging.StreamHandler()]

FLASK_APP_DEBUG = os.environ.get("FLASK_APP_DEBUG", "false").lower() == "true"

