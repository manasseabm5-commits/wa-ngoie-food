# -*- coding: utf-8 -*-
"""
🌱 SCRIPT D'INITIALISATION ET D'INJECTION DE DONNÉES DE TEST (PROD 2026)
Développé pour Wa Ngoie Food par l'expert Manassé ABM
"""

from app import app
from model import db, User, Commande, IATraining

def initialiser_systeme():
    if "postgresql" in app.config['SQLALCHEMY_DATABASE_URI']:
        print("⚠️ DANGER : Vous êtes connecté à la base PostgreSQL de Render !")
        confirmation = input("Voulez-vous VRAIMENT TOUT SUPPRIMER en production ? (oui/non) : ")
        if confirmation.strip().lower() != "oui":
            print("❌ Opération annulée pour protéger la production.")
            return

    print("🚀 Début de l'initialisation de la base de données Wa Ngoie Food...")
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ Tables SQL recréées avec succès.")

        # CONFIGURATION DES NOUVEAUX IDENTIFIANTS MAÎTRES REQUIS
        admin_user = User(
            username="wangoie",
            phone="243831674115",
            is_student_isipa=False
        )
        admin_user.set_password("cbfw4life")
        db.session.add(admin_user)
        print("👤 Compte Administrateur configuré (Login: wangoie / MDP: cbfw4life).")

        etudiant_user = User(
            username="Manasse_ABM",
            phone="0820000000",
            is_student_isipa=True
        )
        etudiant_user.set_password("etudiant2026")
        db.session.add(etudiant_user)
        db.session.commit()

        print("\n🎉 Base de données initialisée avec succès ! Tout est prêt pour la production.")

if __name__ == '__main__':
    initialiser_systeme()
