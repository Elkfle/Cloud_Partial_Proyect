import uuid;
from . import db;
from datetime import datetime, timedelta
from flask import current_app;
from itsdangerous import URLSafeTimedSerializer as Serializer;

#===: user class :===
class User(db.Model):
    __tablename__ = 'user_table';
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"), unique=True);
    nickname = db.Column(db.String(20), nullable=False, unique=True);
    email = db.Column(db.String(80), nullable=False, unique=True);
    password = db.Column(db.String(80), nullable=False, unique=False);
    reset_password_token = db.Column(db.String(255), default=None);
    reset_password_token_expires_at = db.Column(db.DateTime , default=datetime.utcnow());
    bank = db.Column(db.Integer(), nullable=False, unique=False, default=0);
    creationDate = db.Column(db.DateTime, default=datetime.utcnow());
    imageProfile = db.Column(db.String(255), default=None);
    
    def __init__(self, nickname, email, password, bank=0):
        self.nickname = nickname;
        self.email = email;
        self.password = password;
        self.reset_password_token = None;
        self.reset_password_token_expires_at = datetime.utcnow();
        self.bank = bank;
        self.imageProfile = None;
        self.creationDate = datetime.utcnow();
        
    def serialize(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'email': self.email,
            'password': self.password,
            'bank': self.bank,
            'imageProfile': self.imageProfile,
            'creationDate': self.creationDate,
        };
        
    def get_reset_password_token(self, expires_sec=600):
        s = Serializer(str(current_app.config['SECRET_KEY']), expires_sec);
        token = s.dumps({'user_id': self.id}).decode('utf-8');
        
        self.reset_password_token = token;
        self.reset_password_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_sec);
        db.session.commit();
        return token;
    
    @staticmethod
    def verify_reset_password_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try: user_id = s.loads(token)['user_id']
        except: return None;
        
        user = User.query.get(user_id);
        if user is None or user.reset_password_token != token or user.reset_password_token_expires_at < datetime.utcnow(): return None;
        return user;