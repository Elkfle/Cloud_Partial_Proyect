import os;
import config;

from flask import Flask;
from flask_cors import CORS;
from flask_bcrypt import Bcrypt;
from flask_jwt_extended import JWTManager;
from flask_mail import Mail;
from flask_sqlalchemy import SQLAlchemy;

db = SQLAlchemy();
jwt = JWTManager();
mail = Mail();
bcrypt = Bcrypt();

def create_app():
    app = Flask(__name__)
    CORS(app, origins='*', supports_credentials=True);

    # --> configuracion inicial importada como variable de entorno
    environment_configuration = os.environ.get("CONFIGURATION_SETUP");
    app.config.from_object(environment_configuration)

    jwt.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)

    with app.app_context():
        # -> registaer el blueprint necesario para usuarios
        from .user_api import user_api_blueprint;
        app.register_blueprint(user_api_blueprint);
        
        db.create_all();
        return app;