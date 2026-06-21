# -*- coding: utf-8 -*-
"""
⚙️ APPLICATION WA NGOIE FOOD - ARCHITECTURE DES MODÈLES ORM (PROD 2026)
Conçu par l'expert en ingénierie logicielle Manassé ABM
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialisation de l'instance SQLAlchemy (sera liée à l'app dans app.py)
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """
    👤 TABLE UTILISATEURS : Gère les clients, les étudiants ISIPA et l'administrateur
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)  # Clé unique liée au téléphone pour Kinshasa
    password_hash = db.Column(db.String(256), nullable=False)
    is_student_isipa = db.Column(db.Boolean, default=False, nullable=False)    # Filtre programme fidélité ISIPA
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations bi-directionnelles
    commandes = db.relationship('Commande', backref='client', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Chiffre le mot de passe avant insertion"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie le mot de passe lors de la connexion"""
        return check_password_hash(self.password_hash, password)


class Commande(db.Model):
    """
    📦 TABLE COMMANDES : Flux logistique centralisé avec calcul des paniers et statuts
    """
    __tablename__ = 'commandes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    contenu_panier = db.Column(db.Text, nullable=False)      # Stockage sémantique du récapitulatif (ex: "2x Chawarma, 1x Eau")
    total_brut = db.Column(db.Integer, nullable=False)       # Prix total avant remise en Francs Congolais (FC)
    total_final = db.Column(db.Integer, nullable=False)      # Prix appliqué après calculs (Remises étudiantes, etc.)
    adresse_livraison = db.Column(db.String(255), default="À récupérer sur place / ISIPA")
    
    # Statuts gérés par le Dashboard et surveillés par l'IA :
    # "En cuisine", "En route", "Arrivé à l'ISIPA", "Livré", "Client Insiste !"
    statut = db.Column(db.String(50), default="En cuisine", nullable=False)
    
    date_commande = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Formate l'objet pour les requêtes asynchrones JSON du Dashboard Admin"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.client.username,
            "phone": self.client.phone,
            "contenu": self.contenu_panier,
            "total_brut": self.total_brut,
            "total_final": self.total_final,
            "adresse": self.adresse_livraison,
            "status": self.statut,
            "date": self.date_commande.strftime("%d/%m/%Y %H:%M")
        }


class IATraining(db.Model):
    """
    🧠 TABLE ENTRAÎNEMENT IA : Centre d'apprentissage continu pour les mauvaises réponses de l'IA
    """
    __tablename__ = 'ia_training'

    id = db.Column(db.Integer, primary_key=True)
    telephone_client = db.Column(db.String(20), nullable=True)
    message_client = db.Column(db.Text, nullable=False)       # Ce que le client a écrit (Argot, faute, Lingala)
    mauvaise_reponse = db.Column(db.Text, nullable=True)      # L'erreur commise par l'IA avant correction
    bonne_reponse = db.Column(db.Text, nullable=False)        # La correction logique injectée par Manassé ABM
    corrige = db.Column(db.Boolean, default=False, nullable=False)
    date_signalement = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Formate l'anomalie pour l'affichage dans l'interface de dressage unique"""
        return {
            "id": self.id,
            "telephone": self.telephone_client if self.telephone_client else "Anonyme",
            "message_client": self.message_client,
            "mauvaise_reponse": self.mauvaise_reponse if self.mauvaise_reponse else "Non comprise",
            "bonne_reponse": self.bonne_reponse,
            "date": self.date_signalement.strftime("%d/%m/%Y à %H:%M")
        }
