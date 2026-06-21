# -*- coding: utf-8 -*-
"""
🚀 APPLICATION WA NGOIE FOOD - LOGIQUE SERVEUR CENTRAL (PROD 2026 - LOGISTIQUE AVANCÉE)
Développé par l'expert Manassé ABM
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from model import db, User, Commande, IATraining

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def home(): return render_template('index.html', page_class='bg-restaurant')

@app.route('/menu')
def menu(): return render_template('menu.html', page_class='bg-menu')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('chat'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username', '').strip()).first()
        if user and user.check_password(request.form.get('password', '')):
            login_user(user)
            return redirect(url_for('chat'))
    return render_template('login.html', page_class='bg-auth')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form.get('username').strip(), phone=request.form.get('phone').strip(), is_student_isipa='is_student_isipa' in request.form)
        new_user.set_password(request.form.get('password'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', page_class='bg-auth')

@app.route('/logout')
def logout(): logout_user(); return redirect(url_for('home'))

@app.route('/chat')
@login_required
def chat():
    commandes = Commande.query.filter_by(user_id=current_user.id).order_by(Commande.id.desc()).all()
    return render_template('chat.html', page_class='bg-menu', commandes=commandes)

# --- ENDPOINTS LOGISTIQUES ET SÉCURITÉ TUNNEL ---

@app.route('/api/chat/message', methods=['POST'])
@login_required
def ai_message():
    message_client = request.form.get('message', '').strip()
    msg_lower = message_client.lower()

    if any(plat in msg_lower for plat in ["chawarma", "hamburger", "tacos", "poulet", "frites"]):
        total_brut = 14000
        if "hamburger" in msg_lower: total_brut = 16000
        elif "poulet" in msg_lower: total_brut = 28000
        
        remise = int(total_brut * 0.10) if current_user.is_student_isipa else 0
        total_final = total_brut - remise

        # L'IA génère le panier et injecte un bouton d'action JavaScript au lieu d'enregistrer direct
        reponse_ia = (
            f"📋 **Votre Panier Wa Ngoie Food** :\n"
            f"- 1x {message_client.capitalize()}\n\n"
            f"💰 Total Brut : {total_brut:,} FC\n"
            f"🎓 Remise ISIPA : -{remise:,} FC\n"
            f"💵 **Total Net : {total_final:,} FC**\n\n"
            f"Confirmez votre choix pour envoyer les informations au gérant :\n\n"
            f"<button class='btn-trigger-confirm' onclick=\"confirmerEtAjouterCommande('1x {message_client}', {total_brut}, {total_final})\" style='background:#25d366; color:#131314; font-weight:bold; border:none; padding:10px 16px; border-radius:8px; cursor:pointer; display:none;'>🟢 Valider & Envoyer sur WhatsApp</button>"
        )
        return jsonify({"status": "success", "role": "model", "response": reponse_ia})

    return jsonify({"status": "success", "role": "model", "response": "Posez-moi une question sur les plats disponibles."})

@app.route('/api/commande/creer', methods=['POST'])
@login_required
def creer_commande():
    # Enregistrement strict uniquement lorsque l'utilisateur valide l'action
    cmd = Commande(
        user_id=current_user.id,
        contenu_panier=request.form.get('contenu'),
        total_brut=int(request.form.get('total_brut')),
        total_final=int(request.form.get('total_final')),
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
    return render_template('ia_training.html', erreurs=erreurs, total_corriges=0, precision_ia=95)

@app.route('/admin/commandes')
@login_required
def api_admin_commandes():
    return jsonify([c.to_dict() for c in Commande.query.order_by(Commande.id.desc()).all()])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
