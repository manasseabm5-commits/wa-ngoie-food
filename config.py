# config.py
import os

class Config:
    # Sécurité de l'application Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cle_secrete_wa_ngoie_abm_ai_2026_prod'
    
    # --- MODIFICATION CRITIQUE RENDER : CONNEXION POSTGRESQL PERMANENTE ---
    # Récupère automatiquement l'URL de Render en production, ou utilise ton URL collée par défaut
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'REMPLACE_CE_TEXTE_PAR_TON_EXTERNAL_OU_INTERNAL_DATABASE_URL_DE_RENDER'
    
    # Correctif technique obligatoire : SQLAlchemy exige 'postgresql://' au lieu de 'postgres://'
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration des dossiers de stockage statique
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limite à 16 Mo max par fichier
    
    # Informations officielles de l'établissement Wa Ngoie Food
    ADRESSE_RESTO = "Avenue OUA, coin Komoriko numéro 14, Kintambo (Référence : ISIPA)"
    TELEPHONE_OFFICIEL_WHATSAPP = "243831674115"
    INGENIEUR_CREATEUR = "Manassé ABM"
    
    # Mapping strict des articles officiels vers leurs visuels dans static/images/
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
