from flask import Blueprint;

games_api_blueprint = Blueprint('games_api', __name__);

# --> importar las rutas usando el blueprint actual
from . import routes;