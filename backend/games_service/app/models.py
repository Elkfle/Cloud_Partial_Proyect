import uuid;
from . import db;
from datetime import datetime, timedelta
from flask import current_app;
from itsdangerous import URLSafeTimedSerializer as Serializer;


#===: games class :===
class Game(db.Model):
    __tablename__ = 'game_table';
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"), unique=True);
    alias = db.Column(db.String(255), nullable=False);
    name = db.Column(db.String(255), nullable=False);
    description = db.Column(db.Text, nullable=True);
    imageGame = db.Column(db.String(255), default=None);
    def __init__(self, alias, name, description, imageGame):
        self.alias = alias;
        self.name = name;
        self.description = description;
        self.imageGame = imageGame;
    def serialize(self):
        return {
            'id': self.id,
            'alias': self.alias,
            'name': self.name,
            'description': self.description,
            'imageGame': self.imageGame,
        };

#===: transaction class :===
class Transaction(db.Model):
    __tablename__ = 'transaction_table';
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"), unique=True);
    user_id = db.Column(db.String(36), nullable=False)  # Identificador único del usuario
    quantityDollar = db.Column(db.Integer(), nullable=False, unique=False);
    creationDate = db.Column(db.DateTime, default=datetime.utcnow());
    
    def __init__(self, user_id, quantityDollar):
        self.user_id = user_id
        self.quantityDollar = quantityDollar;
        self.creationDate = datetime.utcnow();
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quantityDollar': self.quantityDollar,
            'creationDate': self.creationDate,
        };

#===: roulette bet :===
class RouletteBet(db.Model):
    __tablename__ = 'roulette_bet_table'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"), unique=True)
    user_id = db.Column(db.String(36), nullable=False)  # Identificador único del usuario
    bet_data = db.Column(db.Text, nullable=False)  # JSON, bets as a list of dicts {'type': 'xx', 'value': 00, 'amount': 00} 
    result = db.Column(db.String(50), nullable=True)  # 'win', 'lose', or None if the bet hasn't been resolved yet
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, user_id, bet_data):
        self.user_id = user_id
        self.bet_data = bet_data

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bet_data': self.bet_data,
            'result': self.result,
            'timestamp': self.timestamp,
        }