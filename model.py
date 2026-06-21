# model.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_student_isipa = db.Column(db.Boolean, default=False)
    date_inscription = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    conversations = db.relationship('Conversation', backref='client', lazy=True)

class Commande(db.Model):
    __tablename__ = 'commande'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    adresse_livraison = db.Column(db.Text, nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    total_brut = db.Column(db.Float, nullable=False)
    frais_livraison = db.Column(db.Float, default=0.0)
    total_final = db.Column(db.Float, nullable=False)
    livreur_assigne = db.Column(db.String(50), nullable=True)
    statut = db.Column(db.String(50), default="En attente")
    date_creation = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Conversation(db.Model):
    __tablename__ = 'conversation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    titre = db.Column(db.String(100), default="Nouvelle Discussion")
    date_creation = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    est_supprime = db.Column(db.Boolean, default=False)
    
    messages = db.relationship('MessageHistory', backref='conversation', lazy=True)

class MessageHistory(db.Model):
    __tablename__ = 'message_history'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    date_envoi = db.Column(db.DateTime, default=datetime.datetime.utcnow)
