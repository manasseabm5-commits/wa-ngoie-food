# model.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Table de gestion des comptes clients et administrateurs de Wa Ngoie Food."""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_student_isipa = db.Column(db.Boolean, default=False)  # Mode budget étudiant ISIPA
    date_inscription = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relations
    conversations = db.relationship('Conversation', backref='client', lazy=True)

class Commande(db.Model):
    """Table de stockage centralisée des flux logistiques affichés sur le tableau de bord admin."""
    __tablename__ = 'commande'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    adresse_livraison = db.Column(db.Text, nullable=False)
    contenu = db.Column(db.Text, nullable=False)  # Liste des plats séparés par des virgules
    total_brut = db.Column(db.Float, nullable=False)
    frais_livraison = db.Column(db.Float, default=0.0)
    total_final = db.Column(db.Float, nullable=False)
    livreur_assigne = db.Column(db.String(50), nullable=True)  # Suivi des courseurs (Serge, Christian, etc.)
    statut = db.Column(db.String(50), default="En attente")  # En attente, En cuisine, En livraison, Livré
    date_creation = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Conversation(db.Model):
    """Table stockant les discussions créées dans la sidebar gauche à la manière de Gemini."""
    __tablename__ = 'conversation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    titre = db.Column(db.String(100), default="Nouvelle Discussion")
    date_creation = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    est_supprime = db.Column(db.Boolean, default=False)
    
    # Relations
    messages = db.relationship('MessageHistory', backref='conversation', lazy=True)

class MessageHistory(db.Model):
    """Historique pas-à-pas des bulles de texte échangées entre le client et l'IA."""
    __tablename__ = 'message_history'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' ou 'model' (style Gemini)
    contenu = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)  # Lien si l'utilisateur télécharge une photo
    date_envoi = db.Column(db.DateTime, default=datetime.datetime.utcnow)
