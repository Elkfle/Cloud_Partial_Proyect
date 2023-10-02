import os
from dotenv import load_dotenv;

# -> verificar que exista el .env 
dotenv_path = os.path.join(os.path.dirname(__file__), '.env');
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class DevelopmentConfig:
    DEBUG = True;
    JWT_SECRET_KEY = 'pass';
    JWT_ACCESS_TOKEN_EXPIRES = False;
    MAIL_SERVER = "smtp.gmail.com";
    MAIL_PORT = 587;
    MAIL_USE_TLS = True;
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME');
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD');
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://maestro:AtxGYESGBEVNZ2GAbsAC@database-proy.cdxuyfen8rhu.us-east-1.rds.amazonaws.com:5432/tumipalace_db_development_games";
    SECRET_KEY = "dev_secret_key";
    UPLOAD_FOLDER = "static/users";