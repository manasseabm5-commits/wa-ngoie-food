import os

class Config:
    # Clé secrète pour sécuriser les sessions utilisateur
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-tres-secrete-pour-la-prod-2026'
    
    # Configuration de la base de données SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///wangoie_food.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Dossier pour stocker les photos des clients
    UPLOAD_FOLDER = 'static/uploads'
    
    # Limite de taille pour les photos (ex: 5 Mo)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024