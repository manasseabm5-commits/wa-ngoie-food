# 🍔 Wa Ngoie Food - Plateforme Marchande Multimodale (Prod 2026)

L'écosystème connecté **Wa Ngoie Food** est une infrastructure numérique marchande de niveau international conçue exclusivement pour l'université ISIPA à Kintambo (Kinshasa) [index]. Il combine une vitrine web adaptative haute performance et un assistant sémantique interactif autonome (**ABM AI Engine**) capable de piloter les commandes, calculer les grilles tarifaires locales en Francs Congolais (FC) et acheminer les flux instantanément vers WhatsApp administrateur [index].

---

## 🧠 Architecture Logicielle & Signature
Cette plateforme web hybride a été pensée, structurée et programmée de bout en bout par l'expert en ingénierie logicielle **Manassé ABM** [index]. Elle intègre une logique de tolérance aux pannes réseau (3G/4G faible) et une flexibilité multi-bases de données (SQLite / PostgreSQL) [index].

---

## 🚀 Fonctionnalités Élite Intégrées

### 1. Tunnel de Commande "Text-Driven" Interactif (Oui/Non)
*   **Calcul de Panier en Temps Réel :** L'assistant ABM AI analyse la saisie textuelle ou vocale, applique une remise automatique de 10% pour les étudiants de l'ISIPA Kintambo, et génère un récapitulatif financier fluide [index].
*   **Validation Logistique Sécurisée :** Pour éviter d'encombrer le flux d'administration, la commande s'enregistre avec le statut `"En attente"` uniquement lorsque l'utilisateur tape `"Oui"` dans la discussion [index].
*   **Routage WhatsApp Dynamique :** Détection native de l'appareil (Mobile vs Machine) pour générer l'URL d'ouverture WhatsApp correcte, éliminant définitivement les erreurs d'analyse DNS (`DNS_PROBE_FINISHED_NXDOMAIN`) [index].

### 2. Traitement Multimodal & Accessibilité
*   **Traitement Vocal Autonome :** Intégration de la reconnaissance vocale (`Web Speech API`) configurée sur le français et tolérant les expressions locales courantes [index].
*   **Réception Médias :** Capture et téléversement sécurisé des photos de reçus ou de livraisons (blindé contre les conflits de caractères spéciaux et d'espaces) [index].

### 3. Console d’Administration et Centre d'Entraînement IA
*   **Flux Logistique Asynchrone :** Interrogation asynchrone toutes les 5 secondes pour actualiser les livraisons sans recharger la page [index].
*   **Alertes Sonores Fréquentielles (AudioContext) :** Bip mélodieux lors de l'arrivée d'une commande saine, et alerte stridente en dents de scie si un étudiant en retard clique sur le bouton d'urgence **"🚨 Insister"** [index].
*   **Actions d'Administration :** Boutons d'actions rapides pour modifier le statut du flux (`🍳 Préparer` / `🚴 Livrer`) ou effacer les données (`❌ Supprimer`) [index].
*   **Dresage Continu :** Interface unique permettant d'associer immédiatement une phrase non comprise par l'IA à une réponse chaleureuse définitive [index].

---

## 🛠️ Pile Technique (Tech Stack) & Dépendances
L'architecture s'appuie sur des bibliothèques robustes et légères garantissant une haute disponibilité :
*   **Backend Framework :** Flask 3.0.2 (Python 3.13) [index]
*   **ORM / Base de Données :** Flask-SQLAlchemy + Psycopg2-binary (PostgreSQL en production) [index]
*   **Gestion des Sessions :** Flask-Login (Sécurisation des rôles Admin / Client) [index]
*   **Production WSGI Server :** Gunicorn 21.2.0 (Immunisé contre les serveurs de dev) [index]
*   **Frontend :** HTML5, CSS3 CSS Adaptatif double colonne sur mobile, JavaScript Asynchrone pur (zéro framework lourd) [index].

---

## 📦 Procédure d'Installation et Configuration Locale

1. **Cloner le projet et se positionner dans le répertoire :**
   ```bash
   cd "FAST_FOOD Wa_NGOIE (1)"
   ```

2. **Installer les dépendances requises :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialiser la base de données locale (SQLite) :**
   *Cette commande crée le fichier `wangoie.db`, injecte l'administrateur sécurisé, des commandes de simulation et l'anomalie sémantique d'entraînement.*
   ```bash
   python init_db.py
   ```

4. **Lancer le serveur de développement :**
   ```bash
   python app.py
   ```
   *Accédez à l'application via `http://127.0.0.1:5000` sur votre ordinateur ou tapez votre IP locale pour tester le responsive sur smartphone.*

---

## ☁️ Déploiement Automatique sur Render

L'infrastructure logicielle est configurée pour s'auto-initialiser sur Render de façon **100 % gratuite**, en contournant les limitations d'accès au Shell payant.

1. **Lier le dépôt GitHub** à votre Web Service Render.
2. **Configurer les variables d'environnement (onglet Environment) :**
   *   `DATABASE_URL` : (Généré automatiquement par Render PostgreSQL) [index]
   *   `SECRET_KEY` : `votre_cle_secrete_abm_2026`
3. **Commandes d'infrastructure de Render :**
   *   **Build Command :** `pip install -r requirements.txt`
   *   **Start Command :** `gunicorn app:app`

*Au déploiement, le serveur Flask inspecte la chaîne PostgreSQL de Render, crée l'architecture des tables à la volée, et rend l'application disponible en production.*

---

## 🔑 Identifiants d'Accès Maîtres (Admin Console)
*   **URL de connexion :** `/login`
*   **Identifiant :** `admin`
*   **Mot de passe :** `WaNgoie2026`
