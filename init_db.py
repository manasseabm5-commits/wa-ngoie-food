# -*- coding: utf-8 -*-
"""
🌱 SCRIPT D'INITIALISATION ET DE CONFIGURATION DU SERVEUR MAÎTRE (PROD 2026)
Développé pour Wa Ngoie Food par l'expert Manassé ABM - Version Déploiement Gratuit Automatique
"""

from app import app
from model import db, User

def initialiser_systeme():
    # Correctif d'expert : Plus d'envoi d'input() bloquant pour Render gratuit
    if "postgresql" in app.config['SQLALCHEMY_DATABASE_URI']:
        print("⚠️ Application automatique des nouvelles structures sur PostgreSQL Render...")
    else:
        print("🌱 Initialisation locale de la base de données de test...")

    print("🚀 Démarrage du déploiement des structures de tables Wa Ngoie Food...")
    
    with app.app_context():
        # Reconstruction propre et sémantique des tables SQL
        db.drop_all()
        db.create_all()
        print("✅ Base de données purgée et réinitialisée avec succès.")

        # CONFIGURATION DE L'ACCÈS DU GÉRANT OFFICIEL
        admin_user = User(
            username="wangoie",
            phone="243831674115"
        )
        admin_user.set_password("cbfw4life")
        db.session.add(admin_user)
        print("👤 Compte Gérant Administrateur déployé (Login: wangoie / MDP: cbfw4life).")

        # CONFIGURATION DU COMPTE ARCHITECTE
        architecte_user = User(
            username="Manasse_ABM",
            phone="0820000000"
        )
        architecte_user.set_password("etudiant2026")
        db.session.add(architecte_user)
        
        db.session.commit()
        print("🎉 Déploiement logiciel achevé. L'écosystème Wa Ngoie Food est opérationnel.")

if __name__ == '__main__':
    initialiser_systeme()
