# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cle_secrete_wa_ngoie_abm_ai_2026_prod'
    
    # Récupération sécurisée de la base de données de Render
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Correctif technique obligatoire pour Render / SQLAlchemy
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        
    if not SQLALCHEMY_DATABASE_URI:
        # Fallback local de sécurité si DATABASE_URL est absente
        SQLALCHEMY_DATABASE_URI = 'sqlite:///wangoie.db'
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    ADRESSE_RESTO = "Avenue OUA, coin Komoriko numéro 14, Kintambo (Référence : ISIPA)"
    TELEPHONE_OFFICIEL_WHATSAPP = "243831674115"
    INGENIEUR_CREATEUR = "Manassé ABM"
    
    MENU_IMAGES = {
        "chawarma": "chawarma.jpg", 
        "hamburger": "hamburger.jpg", 
        "tacos": "tacos.jpg",
        "saucisse": "saucisse.jpg", 
        "cuisse": "cuisse.jpg", 
        "poulet mayo": "poulet_mayo.jpg",
        "samoussa": "samoussa.jpg", 
        "boulette": "boulette.jpg", 
        "spaghetti": "spaghetti.jpg",
        "chikwangue": "chikwangue.jpg", 
        "frites": "frites.jpg", 
        "banane": "banane.jpg",
        "eau": "eau.jpg", 
        "sucre": "sucre.jpg", 
        "savanna": "savanna.jpg", 
        "biere": "biere.jpg"
    }
