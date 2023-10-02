from flask import Blueprint;

user_api_blueprint = Blueprint('user_api', __name__);

# --> importar las rutas usando el blueprint actual
from . import routes;