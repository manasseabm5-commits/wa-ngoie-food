# -*- coding: utf-8 -*-
"""
🌱 SCRIPT D'INITIALISATION ET D'INJECTION DE DONNÉES DE TEST (CORRIGÉ)
Développé pour Wa Ngoie Food par l'expert Manassé ABM
"""

from app import app
from model import db, User, Commande, IATraining

def initialiser_systeme():
    # SÉCURITÉ : On vérifie si on est sur Render en inspectant l'URI de la base
    if "postgresql" in app.config['SQLALCHEMY_DATABASE_URI']:
        print("⚠️ DANGER : Vous êtes connecté à la base PostgreSQL de Render !")
        confirmation = input("Voulez-vous VRAIMENT TOUT SUPPRIMER en production ? (oui/non) : ")
        if confirmation.strip().lower() != "oui":
            print("❌ Opération annulée pour protéger la production.")
            return

    print("🚀 Début de l'initialisation de la base de données Wa Ngoie Food...")
    
    with app.app_context():
        # 1. Recréation propre des tables
        db.drop_all()
        db.create_all()
        print("✅ Tables SQL recréées avec succès.")

        # 2. Création du compte Administrateur Élite
        admin_user = User(
            username="admin",
            phone="243831674115",
            is_student_isipa=False
        )
        # Mot de passe sécurisé pour l'accès à votre console
        admin_user.set_password("WaNgoie2026")
        db.session.add(admin_user)
        print("👤 Compte Administrateur configuré (Login: admin / MDP: WaNgoie2026).")

        # 3. Création d'un compte Client de test (Étudiant ISIPA)
        etudiant_user = User(
            username="Manasse_ABM",
            phone="0820000000",
            is_student_isipa=True
        )
        etudiant_user.set_password("etudiant2026")
        db.session.add(etudiant_user)
        
        # Validation immédiate des utilisateurs pour lier les clés étrangères
        db.session.commit()

        # 4. Injection de commandes de test dans le flux logistique
        cmd1 = Commande(
            user_id=etudiant_user.id,
            contenu_panier="2x Chawarma croustillant, 1x Canette Sucrée",
            total_brut=31500,
            total_final=28350,  # Application automatique des 10% ISIPA
            adresse_livraison="Auditoire G2 Informatique - Bâtiment ISIPA Kintambo",
            statut="En cuisine"
        )
        
        cmd2 = Commande(
            user_id=etudiant_user.id,
            contenu_panier="1x Poulet Mayo Entier, 1x Portion de Frites, 2x Eau minérale",
            total_brut=39000,
            total_final=35100,
            adresse_livraison="Avenue OUA n°14, Kintambo",
            statut="Client Insiste !"  # Déclenche l'alarme sonore sur l'interface admin
        )
        
        db.session.add(cmd1)
        db.session.add(cmd2)
        print("📦 Commandes logistiques de test injectées.")

        # 5. Injection d'une anomalie sémantique (CORRECTION : bonne_reponse="" pour éviter l'échec NOT NULL)
        anomalie = IATraining(
            telephone_client="0899999999",
            message_client="naza na posa ya frites na makemba s'il vous plaît",
            mauvaise_reponse="Désolé, je n'ai pas bien compris votre commande de nourriture. Pouvez-vous reformuler ?",
            bonne_reponse="",  # Chaîne vide valide au lieu de None pour respecter la contrainte SQL
            corrige=False
        )
        db.session.add(anomalie)
        print("🧠 Anomalie sémantique injectée dans le centre d'entraînement.")

        # Soumission finale en BDD
        db.session.commit()
        print("\n🎉 Base de données initialisée avec succès ! Tout est prêt pour la production.")

if __name__ == '__main__':
    initialiser_systeme()
