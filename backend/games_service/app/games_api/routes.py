import os;
import json;
import requests;

from random import randint;
from . import games_api_blueprint;
from .. import db;
from flask import (
    request,
    jsonify,
    current_app,
    send_file
);
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required
);
from ..models import (
    Game,
    RouletteBet,
    Transaction
);

# ==> Se agrega la URL del servicio (users_service)
USER_SERVICE_URL = "lb-prod-proy-167809630.us-east-1.elb.amazonaws.com:8000/api/users/";

#===: Get info about User ===:
def get_user_info(user_id):
    response = requests.get(USER_SERVICE_URL + user_id)
    if response.status_code == 200: return response.json()
    else: return None

#===: Handle static image ===:
@games_api_blueprint.route("/api/<path:path>")
def serve_file(path):
    absolute_path = os.path.join(os.getcwd(), path)
    if path.endswith(".png"):
        return send_file(absolute_path, mimetype='image/png')
    if path.endswith(".jpg"):
        return send_file(absolute_path, mimetype='image/jpg')
    elif path.endswith(".mp3"):
        return send_file(absolute_path, mimetype='audio/mpeg')
    else:
        return "File type not supported", 400
    

#===: Handle games ===:
@games_api_blueprint.route("/api/games", methods=["GET"])
def get_games():
    games = Game.query.all()
    return jsonify([game.serialize() for game in games])


#===: Roulette Logic ===:
@games_api_blueprint.route('/api/roulette/bet', methods=['POST'])
@jwt_required()
def place_bet():
    user_id = get_jwt_identity();
    user = get_user_info(user_id)
    if not user: return jsonify({'error': 'El usuario no fue encontrado.'}), 404;
    
    bet_data = request.json.get('bet_data');
    total_bet_amount = sum(bet['amount'] for bet in bet_data);
    if total_bet_amount > user['bank']: 
        return jsonify({'error': 'Los fondos son insuficientes.'}), 400;
    
    bet = RouletteBet(user_id=user_id, bet_data=json.dumps(bet_data));
    user['bank'] = user['bank'] - total_bet_amount;
    
    db.session.add(bet)
    db.session.commit()
    return jsonify(bet.serialize()), 201;

@games_api_blueprint.route('/api/roulette/result', methods=['GET'])
@jwt_required()
def get_result():
    user_id = get_jwt_identity();
    user = get_user_info(user_id)
    if not user: return jsonify({'error': 'El usuario no fue encontrado.'}), 404;
    
    bet_id = request.args.get('bet_id')
    bet = RouletteBet.query.get(bet_id)
    if not bet: return jsonify({'error': 'Apuesta no válida.'}), 404
    
    roulette_number = randint(0, 36)
    roulette_color = 'red' if roulette_number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36] else 'black'
    bet_data = json.loads(bet.bet_data)
    
    for bet_entry in bet_data:
        if (bet_entry['type'] == 'number' and bet_entry['value'] == roulette_number) or (bet_entry['type'] == 'color' and bet_entry['value'] == roulette_color):
            bet_entry['result'] = 'win'
            user.bank += bet_entry['amount'] * 2
        else:
            bet_entry['result'] = 'lose'
    
    bet.result = 'win' if any(entry['result'] == 'win' for entry in bet_data) else 'lose'
    result_data = {
        'numbers': roulette_number,
        'color': roulette_color,
        'bet_data': bet_data
    }

    db.session.commit()
    
    return jsonify(result_data), 200;