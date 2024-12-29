import os
from dotenv import load_dotenv
load_dotenv()
from db_manager import MySQLDatabase

#sql_credentials
DB_HOST = "localhost"
DB_PORT = "3306"
DB_USER = "root"
DB_PASSWORD = "Diptiranjan@1"
DB_DATABASE = "student_log"
credentials = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
    "database": DB_DATABASE
}



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
# APP_DIR = os.path.join(BASE_DIR, 'app')
#
LOG_DIR = os.path.join(BASE_DIR, 'logs')
# DATA_DIR = os.path.join(BASE_DIR, 'data')
# DOCUMENT_DIR = os.path.join(BASE_DIR, 'documents')


PORT = 9000
HOST = '0.0.0.0'
DEBUG = False
WORKERS = 2