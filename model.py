# -*- coding: utf-8 -*-
"""
⚙️ APPLICATION WA NGOIE FOOD - ARCHITECTURE DES MODÈLES ORM (PROD 2026)
Conçu par l'expert en ingénierie logicielle Manassé ABM
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

# Initialisation de l'instance SQLAlchemy centrale
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """
    👤 TABLE UTILISATEURS : Centralise les accès clients et l'administrateur
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)  # Canal WhatsApp exclusif pour Kinshasa
    password_hash = db.Column(db.String(256), nullable=False)
    date_inscription = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relation un-à-plusieurs bidirectionnelle avec suppression en cascade
    commandes = db.relationship('Commande', backref='client', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Chiffre de manière sécurisée le mot de passe avant persistance"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie l'empreinte du mot de passe lors des connexions"""
        return check_password_hash(self.password_hash, password)


class Commande(db.Model):
    """
    📦 TABLE COMMANDES : Flux de livraison en temps réel supervisé par ABM AI
    """
    __tablename__ = 'commandes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    contenu_panier = db.Column(db.Text, nullable=False)      # Liste sémantique des articles (ex: "2x Chawarma, 1x Eau")
    total_brut = db.Column(db.Integer, nullable=False)       # Total en Francs Congolais (FC)
    total_final = db.Column(db.Integer, nullable=False)      # Prix net après ajustements comptables administratifs
    adresse_livraison = db.Column(db.String(255), default="À récupérer sur place au restaurant")
    
    # Cycle de vie d'une commande surveillé en direct par le tableau de bord :
    # "En attente", "En cuisine", "En route", "Arrivé à destination", "Livré", "Client Insiste !"
    statut = db.Column(db.String(50), default="En attente", nullable=False)
    date_commande = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        """Sérialise la commande pour alimenter le flux asynchrone JSON du gérant"""
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
    🧠 TABLE ENTRAÎNEMENT IA : Centre névralgique de la mémoire locale autonome d'ABM AI
    """
    __tablename__ = 'ia_training'

    id = db.Column(db.Integer, primary_key=True)
    telephone_client = db.Column(db.String(20), nullable=True)
    message_client = db.Column(db.Text, nullable=False)       # Saisie de l'utilisateur (Argot, fautes, Lingala)
    mauvaise_reponse = db.Column(db.Text, nullable=True)      # Anomalie générée ou "Incompris" avant correction
    bonne_reponse = db.Column(db.Text, nullable=False)        # Instruction ou réponse validée par l'administration
    corrige = db.Column(db.Boolean, default=False, nullable=False)
    date_signalement = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Formate l'anomalie linguistique pour l'interface de dressage admin"""
        return {
            "id": self.id,
            "telephone": self.telephone_client if self.telephone_client else "Anonyme",
            "message_client": self.message_client,
            "mauvaise_reponse": self.mauvaise_reponse if self.mauvaise_reponse else "Non comprise",
            "bonne_reponse": self.bonne_reponse,
            "date": self.date_signalement.strftime("%d/%m/%Y à %H:%M")
        }
