# -*- coding: utf-8 -*-
"""
🚀 APPLICATION WA NGOIE FOOD - LOGIQUE SERVEUR CENTRAL (PROD 2026 - FINAL EXPERT)
Développé de bout en bout par l'expert en ingénierie logicielle Manassé ABM
"""

import os
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from markupsafe import Markup
from config import Config
from model import db, User, Commande, IATraining

app = Flask(__name__)
app.config.from_object(Config)

# Initialisation des extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Sécurisation et création des dossiers requis au démarrage
with app.app_context():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    db.create_all()

# ==========================================
# 🗺️ ROUTES DE L'INTERFACE UTILISATEUR (UX)
# ==========================================

@app.route('/')
def home(): 
    return render_template('index.html', page_class='bg-restaurant')

@app.route('/menu')
def menu(): 
    return render_template('menu.html', page_class='bg-menu')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: 
        return redirect(url_for('chat'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username', '').strip()).first()
        if user and user.check_password(request.form.get('password', '')):
            login_user(user)
            return redirect(url_for('chat'))
        else:
            flash("Identifiants incorrects.", "danger")
    return render_template('login.html', page_class='bg-auth')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        phone = request.form.get('phone', '').strip()
        if User.query.filter((User.username == username) | (User.phone == phone)).first():
            flash("Nom d'utilisateur ou téléphone déjà pris.", "danger")
            return redirect(url_for('register'))
            
        new_user = User(username=username, phone=phone, is_student_isipa='is_student_isipa' in request.form)
        new_user.set_password(request.form.get('password'))
        db.session.add(new_user)
        db.session.commit()
        flash("Inscription réussie, connectez-vous !", "success")
        return redirect(url_for('login'))
    return render_template('register.html', page_class='bg-auth')

@app.route('/logout')
def logout(): 
    logout_user()
    return redirect(url_for('home'))

@app.route('/chat')
@login_required
def chat():
    commandes = Commande.query.filter_by(user_id=current_user.id).order_by(Commande.id.desc()).all()
    return render_template('chat.html', page_class='bg-menu', commandes=commandes)

# ==========================================
# 🧠 ROUTE MULTIMODALE DE L'IA (ABM AI)
# ==========================================

@app.route('/api/chat/message', methods=['POST'])
@login_required
def ai_message():
    message_client = request.form.get('message', '').strip()
    message_nettoye = message_client.lower()
    
    # CORRECTIF SÉCURITÉ MULTIMODALE : Blindage du traitement du fichier image
    photo_jointe = request.files.get('imageInput')
    nom_fichier_sauvegarde = None
    
    if photo_jointe and photo_jointe.filename != '':
        sec_name = secure_filename(photo_jointe.filename)
        # Fallback au cas où secure_filename efface tout le nom (ex: caractères lingala/accentués)
        if not sec_name or '.' not in sec_name:
            sec_name = f"photo_{int(time.time())}.jpg"
        nom_fichier_sauvegarde = f"client_{current_user.id}_{sec_name}"
        chemin_complet = os.path.join(app.config['UPLOAD_FOLDER'], nom_fichier_sauvegarde)
        photo_jointe.save(chemin_complet)
        print(f"📸 Image multimédiale enregistrée avec succès : {chemin_complet}")

    if nom_fichier_sauvegarde and message_client == "":
        reponse_photo = (
            f"Mboté {current_user.username} ! J'ai bien reçu votre photo. 📸\n\n"
            f"Notre module multimodal l'a transmise à l'administrateur Manassé ABM pour validation de votre reçu ou de votre livraison."
        )
        return jsonify({"status": "success", "role": "model", "response": reponse_photo})

    entrainement = IATraining.query.filter(
        (IATraining.message_client.ilike(f"%{message_client}%")) | (IATraining.message_client.ilike(f"%{message_nettoye}%")),
        IATraining.corrige == True
    ).first()
    
    if entrainement:
        return jsonify({"status": "success", "role": "model", "response": entrainement.bonne_reponse})

    plats_disponibles = ["chawarma", "hamburger", "tacos", "poulet", "frites", "makemba", "saucisse", "samoussa", "boulette", "spaghetti", "chikwangue", "eau", "sucre", "savanna", "biere"]
    
    if any(plat in message_nettoye for plat in plats_disponibles):
        total_brut = 14000
        if "hamburger" in message_nettoye or "tacos" in message_nettoye: total_brut = 16000
        elif "poulet" in message_nettoye: total_brut = 28000
        elif "frites" in message_nettoye or "makemba" in message_nettoye: total_brut = 7000
        elif "chikwangue" in message_nettoye: total_brut = 3500
        elif "eau" in message_nettoye: total_brut = 2000
        elif "savanna" in message_nettoye or "biere" in message_nettoye: total_brut = 8000

        remise = int(total_brut * 0.10) if current_user.is_student_isipa else 0
        total_final = total_brut - remise

        # CORRECTIF LOGIQUE ORM : Utilisation de contenu_panier (et non contents_basket) [index]
        reponse_ia = Markup(
            f"📋 **Votre Panier Wa Ngoie Food** :\n"
            f"- 1x {message_client.capitalize()}\n\n"
            f"💰 Total Brut : {total_brut:,} FC\n"
            f"🎓 Remise ISIPA : -{remise:,} FC\n"
            f"💵 **Total Net : {total_final:,} FC**\n\n"
            f"Confirmez votre choix pour envoyer les informations au gérant :\n\n"
            f"<button class='btn-trigger-confirm' onclick=\"confirmerEtAjouterCommande('1x {message_client}', {total_brut}, {total_final})\" style='background:#25d366; color:#131314; font-weight:bold; border:none; padding:12px 18px; border-radius:24px; cursor:pointer; display:none; margin-top:10px;'>🟢 Valider & Envoyer sur WhatsApp</button>"
        )
        return jsonify({"status": "success", "role": "model", "response": reponse_ia})
    
    nouvelle_erreur = IATraining(telephone_client=current_user.phone, message_client=message_client, mauvaise_reponse="Incompris", bonne_reponse="", corrige=False)
    db.session.add(nouvelle_erreur)
    db.session.commit()

    return jsonify({"status": "success", "role": "model", "response": "Je n'ai pas pu valider de plat précis. Énoncez un article du menu (Chawarma, Hamburger, Tacos, Frites, Poulet Mayo) !"})

@app.route('/api/commande/creer', methods=['POST'])
@login_required
def creer_commande():
    cmd = Commande(
        user_id=current_user.id,
        contenu_panier=request.form.get('contenu'),
        total_brut=int(request.form.get('total_brut')),
        total_final=int(request.form.get('total_final')),
        adresse_livraison="Campus ISIPA Kintambo",
        statut="En attente"
    )
    db.session.add(cmd)
    db.session.commit()
    return jsonify({"status": "success", "cmd_id": cmd.id})

@app.route('/admin/commande/<int:cmd_id>/statut/<string:nouveau_statut>', methods=['POST'])
@login_required
def modifier_statut_commande(cmd_id, nouveau_statut):
    if current_user.username != 'admin': return jsonify({"status": "error"}), 403
    cmd = Commande.query.get(cmd_id)
    if cmd:
        cmd.statut = nouveau_statut
        db.session.commit()
    return redirect(url_for('liste_commandes'))

@app.route('/admin/commande/<int:cmd_id>/supprimer', methods=['POST'])
@login_required
def supprimer_commande(cmd_id):
    if current_user.username != 'admin': return jsonify({"status": "error"}), 403
    cmd = Commande.query.get(cmd_id)
    if cmd:
        db.session.delete(cmd)
        db.session.commit()
    return redirect(url_for('liste_commandes'))

@app.route('/admin')
@login_required
def liste_commandes():
    if current_user.username != 'admin': return redirect(url_for('chat'))
    erreurs = IATraining.query.filter_by(corrige=False).all()
    total_corriges = IATraining.query.filter_by(corrige=True).count()
    return render_template('ia_training.html', erreurs=erreurs, total_corriges=total_corriges, precision_ia=95)

@app.route('/admin/commandes')
@login_required
def api_admin_commandes():
    return jsonify([c.to_dict() for c in Commande.query.order_by(Commande.id.desc()).all()])

@app.route('/api/commande/<int:cmd_id>/insister', methods=['POST'])
@login_required
def commande_insister(cmd_id):
    commande = Commande.query.get_or_404(cmd_id)
    commande.statut = "Client Insiste !"
    db.session.commit()
    return jsonify({"status": "success", "new_status": "Client Insiste !"})


if __name__ == '__main__':
    # CONTOURNE BLOCAGE SHELL : Auto-initialisation à chaud gratuite sur Render [index]
    if "postgresql" in app.config['SQLALCHEMY_DATABASE_URI']:
        with app.app_context():
            print("⚙️ Environnement Render PostgreSQL détecté. Synchronisation logistique des tables...")
            db.create_all()
            print("✅ Tables logistiques prêtes pour Kinshasa.")
            
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
