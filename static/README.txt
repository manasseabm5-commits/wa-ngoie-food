========================================================================
             APPLICATION DE GESTION DE COMMANDE - ABM AI
                      Pour : Wa Ngoie Fast Food
========================================================================

Développé par : Manassé AKONDA
Technologies : Flask (Python), SQLite, Google Gemini API (Gratuit)

Ce projet est une application web complète qui permet aux clients de passer 
des commandes au restaurant par texte ou par la voix grâce à l'assistant 
intelligent "ABM AI". Dès que la commande est complète, l'IA génère un 
bouton pour envoyer le récapitulatif directement sur le WhatsApp du restaurant.

------------------------------------------------------------------------
1. STRUCTURE DU PROJET
------------------------------------------------------------------------
Assurez-vous que l'organisation des dossiers ressemble à ceci :

votre_projet/
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── menu.html
│   ├── login.html
│   ├── register.html
│   ├── chat.html
│   └── admin_commandes.html
│
├── app.py
├── models.py
├── config.py
├── .env
└── requirements.txt

------------------------------------------------------------------------
2. INSTALLATION ET PRÉREQUIS
------------------------------------------------------------------------
Étape 1 : Télécharger et installer Python sur l'ordinateur.
Étape 2 : Ouvrir le terminal ou l'invite de commande dans ce dossier.
Étape 3 : Installer toutes les dépendances nécessaires en tapant :

    pip install -r requirements.txt

------------------------------------------------------------------------
3. CONFIGURATION DE L'IA GRATUITE (GOOGLE GEMINI)
------------------------------------------------------------------------
Pour que l'assistant fonctionne, vous devez ajouter une clé API Google :
1. Rendez-vous sur Google AI Studio : https://google.com
2. Connectez-vous avec un compte Google et cliquez sur "Get API Key".
3. Créez une clé gratuite et copiez-la.
4. Ouvrez le fichier ".env" présent à la racine du projet et collez-la :

    GEMINI_API_KEY=votre_cle_google_ici
    SECRET_KEY=cbfw4life

------------------------------------------------------------------------
4. LANCEMENT ET PREMIER COMPTE ADMISTRATEUR
------------------------------------------------------------------------
1. Dans votre terminal, lancez le serveur : python app.py
2. Ouvrez votre navigateur internet sur : http://127.0.0
3. Cliquez sur "S'inscrire".
4. Créez un compte avec le nom d'utilisateur EXACT : admin
   (Le système reconnaîtra automatiquement ce nom pour lui ouvrir l'accès gérant).
5. Une fois connecté avec le compte "admin", un bouton orange "Commandes Reçues" 
   apparaîtra comme par magie dans la barre de navigation. Les clients ordinaires 
   ne pourront pas voir ce bouton.

------------------------------------------------------------------------
5. FONCTIONNALITÉS EXCLUSIVES INCLUSES
------------------------------------------------------------------------
- Inscription par Numéro de Téléphone (adapté pour Kinshasa).
- Assistant Vocal ABM AI : Écoute le client via le micro du téléphone 
  ou de l'ordinateur et lui parle à haute voix.
- Mode de Secours Local : Si la connexion internet ou l'API coupe, 
  l'application bascule automatiquement sur un système interne par 
  mots-clés pour continuer à répondre au menu, adresses et horaires.
- Bouton WhatsApp Automatique : Génère un lien direct vers le numéro 
  du restaurant (+243831674115) avec la commande pré-remplie.
- Panneau d'administration : Sécurisé et intégré à la barre de navigation 
  pour le compte "admin" afin de suivre l'historique de toutes les commandes.

========================================================================
                         Fin du document
========================================================================
