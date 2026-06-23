import os
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from model import db, User, Commande, IATraining
from utils_ai import analyser_commande_phrase

app = Flask(__name__)
app.config.from_object(Config)

# Initialisation des extensions ORM et de la gestion de session
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Creation automatique des dossiers et des tables SQL au demarrage
with app.app_context():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    db.create_all()


# ROUTES DE L'INTERFACE UTILISATEUR


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
            flash("Nom d'utilisateur ou telephone deja pris.", "danger")
            return redirect(url_for('register'))
        
        new_user = User(username=username, phone=phone)
        new_user.set_password(request.form.get('password'))
        db.session.add(new_user)
        db.session.commit()
        flash("Inscription reussie, connectez-vous !", "success")
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


# MOTEUR DE DISCUSSION AUTONOME ABM AI

@app.route('/api/chat/message', methods=['POST'])
@login_required
def ai_message():
    message_client = request.form.get('message', '').strip()
    message_nettoye = message_client.lower()
    
    # Gestion de la reception des photos envoyees par le client
    photo_jointe = request.files.get('imageInput')
    if photo_jointe and photo_jointe.filename != '':
        sec_name = secure_filename(photo_jointe.filename)
        if not sec_name or '.' not in sec_name:
            sec_name = f"photo_{int(time.time())}.jpg"
        nom_fichier_sauvegarde = f"client_{current_user.id}_{sec_name}"
        chemin_complet = os.path.join(app.config['UPLOAD_FOLDER'], nom_fichier_sauvegarde)
        photo_jointe.save(chemin_complet)
        
        reponse_photo = f"Mbote {current_user.username} ! J'ai bien recu votre photo. Votre document a ete envoye directement au gerant pour validation."
        return jsonify({"status": "success", "role": "model", "response": reponse_photo})

    # 1. Verification si le message a deja ete appris via l'administration
    entrainement = IATraining.query.filter(
        (IATraining.message_client.ilike(f"%{message_client}%")) | (IATraining.message_client.ilike(f"%{message_nettoye}%")),
        IATraining.corrige == True
    ).order_by(IATraining.id.desc()).first()
    
    if entrainement:
        return jsonify({"status": "success", "role": "model", "response": entrainement.bonne_reponse})

    # 2. Dictionnaire des salutations et connaissances de l'entreprise
    salutations = ["mbote", "mbote", "bonjour", "salut", "coucou", "hey", "hello", "sango nini"]
    if any(mot in message_nettoye for mot in salutations):
        return jsonify({"status": "success", "role": "model", "response": f"Mbote {current_user.username} ! Bienvenue chez Wa Ngoie Food. Que desirez-vous manger ou boire aujourd'hui ?"})

    mots_menu = ["menu", "carte", "tarif", "prix", "manger", "boire", "acheter", "liste", "carte", "plats", "boisson"]
    if any(mot in message_nettoye for mot in mots_menu) and not any(p in message_nettoye for p in ["chawarma", "hamburger", "tacos", "poulet", "frites", "makemba", "eau"]):
        reponse_menu = (
            "Menu Officiel Wa Ngoie Food :<br><br>"
            "Nos Specialites Salees :<br>"
            "- Poulet Mayo Entier : 28.000 FC<br>"
            "- Hamburger Juteux : 16.000 FC<br>"
            "- Tacos Genereux : 16.000 FC<br>"
            "- Chawarma croustillant : 14.000 FC<br>"
            "- Saucisse (2 pcs) / Cuisse de poulet (2 pcs) / Samoussa / Boulette / Spaghetti : 14.000 FC<br>"
            "- Portion de Frites / Banane frite (Makemba) : 7.000 FC<br>"
            "- Chikwangue fraiche : 3.500 FC<br><br>"
            "Nos Boissons Fraiches :<br>"
            "- Savanna Cider : 8.000 FC<br>"
            "- Canette Sucree : 3.500 FC<br>"
            "- Biere Locale : 4.000 FC<br>"
            "- Eau minerale fraiche : 2.000 FC<br><br>"
            "Dites-moi simplement ce qui vous fait plaisir pour passer commande !"
        )
        return jsonify({"status": "success", "role": "model", "response": reponse_menu})


    mots_adresse = ["adresse", "ou se trouve", "situe", "emplacement", "lieu", "kintambo", "avenue", "quartier"]
    if any(mot in message_nettoye for mot in mots_adresse):
        return jsonify({"status": "success", "role": "model", "response": "Le restaurant Wa Ngoie Food se situe a l'Avenue OUA, coin Komoriko numero 14, a Kintambo, Kinshasa. Vous pouvez venir recuperer votre plat ou demander une livraison !"})

    mots_createur = ["createur", "cree", "invente", "fait par", "architecte", "developpeur", "manasse", "abm", "patron"]
    if any(mot in message_nettoye for mot in mots_createur):
        return jsonify({"status": "success", "role": "model", "response": "J'ai ete entierement concu, code et optimise par l'expert en ingenierie logicielle Manasse ABM !"})

    mots_presentation = ["qui es-tu", "presente", "tu es qui", "ton nom", "abm ai", "assistant", "robot", "ia"]
    if any(mot in message_nettoye for mot in mots_presentation):
        return jsonify({"status": "success", "role": "model", "response": "Je suis ABM AI, l'assistant virtuel officiel de Wa Ngoie Food. Je vous aide a consulter le menu, calculer vos paniers et valider vos commandes en temps reel !"})

    # Commandes rapides de validation textuelle
    if message_nettoye in ["oui", "o", "yes", "valider", "confirmer", "ok"]:
        return jsonify({"status": "trigger_order", "role": "model", "response": "Parfait ! J'enregistre immediatement votre commande dans le systeme..."})
    elif message_nettoye in ["non", "n", "no", "annuler"]:
        return jsonify({"status": "success", "role": "model", "response": "Commande annulee avec succes. Que desirez-vous d'autre ?"})

    # 3. Analyse semantique des plats et calcul du panier
    panier, total = analyser_commande_phrase(message_client)
    if panier:
        contenu_str = ", ".join(panier)
        reponse_ia = (
            f"Votre Panier Wa Ngoie Food :\n"
            f"- {contenu_str.upper()}\n\n"
            f"Total Net : {total:,} FC\n\n"
            f"Souhaitez-vous valider cette commande ?"
        )
        return jsonify({
            "status": "success", 
            "role": "model", 
            "response": reponse_ia,
            "metadata": {"contenu": contenu_str, "brut": total, "final": total}
        })
    
    # 4. Enregistrement des incompris pour amelioration future par l'admin
    db.session.add(IATraining(telephone_client=current_user.phone, message_client=message_client, mauvaise_reponse="Incompris", bonne_reponse="", corrige=False))
    db.session.commit()
    
    return jsonify({"status": "success", "role": "model", "response": "Mbote ! Je n'ai pas bien saisi. Enoncez clairement les articles que vous voulez commander ou ecrivez 'menu' pour voir la carte !"})

# TRAITEMENT ET INTERACTION DES COMMANDES

@app.route('/api/commande/creer', methods=['POST'])
@login_required
def creer_commande():
    cmd = Commande(
        user_id=current_user.id,
        contenu_panier=request.form.get('contenu'),
        total_brut=int(request.form.get('total_brut')),
        total_final=int(request.form.get('total_final')),
        adresse_livraison="A recuperer au restaurant",
        statut="En attente"
    )
    db.session.add(cmd)
    db.session.commit()
    return jsonify({"status": "success", "cmd_id": cmd.id})

@app.route('/api/commande/<int:cmd_id>/insister', methods=['POST'])
@login_required
def insister_commande(cmd_id):
    cmd = db.session.get(Commande, cmd_id)
    if cmd and cmd.user_id == current_user.id:
        cmd.statut = "Client Insiste !"
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 444

# ==========================================
# PANNEAU DE CONTROLE ADMINISTRATEUR
# ==========================================

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.username != 'wangoie':
        return redirect(url_for('home'))
    toutes_les_err = IATraining.query.filter_by(corrige=False).order_by(IATraining.id.desc()).all()
    total_ok = IATraining.query.filter_by(corrige=True).count()
    return render_template('admin.html', erreurs=toutes_les_err, total_corriges=total_ok)

@app.route('/admin/commandes')
@login_required
def admin_flux_commandes():
    if current_user.username != 'wangoie':
        return jsonify([]), 403
    commandes = Commande.query.order_by(Commande.id.desc()).all()
    return jsonify([c.to_dict() for c in commandes])

@app.route('/admin/commande/<int:cmd_id>/statut/<string:nouveau_statut>', methods=['POST'])
@login_required
def modifier_statut_commande(cmd_id, nouveau_statut):
    if current_user.username != 'wangoie':
        return jsonify({"status": "error"}), 403
    cmd = db.session.get(Commande, cmd_id)
    if cmd:
        cmd.statut = nouveau_statut
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "not_found"}), 404

@app.route('/admin/commande/<int:cmd_id>/supprimer', methods=['POST'])
@login_required
def supprimer_commande(cmd_id):
    if current_user.username != 'wangoie':
        return jsonify({"status": "error"}), 403
    cmd = db.session.get(Commande, cmd_id)
    if cmd:
        db.session.delete(cmd)
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "not_found"}), 404

@app.route('/admin/ia/entrainer', methods=['POST'])
@login_required
def entrainer_ia_admin():
    if current_user.username != 'wangoie':
        return jsonify({"status": "error"}), 403
    phrase_cle = request.form.get("phrase", "").strip()
    reponse_cle = request.form.get("reponse", "").strip()
    if phrase_cle and reponse_cle:
        ia_log = IATraining.query.filter_by(message_client=phrase_cle, corrige=False).first()
        if ia_log:
            ia_log.bonne_reponse = reponse_cle
            ia_log.corrige = True
        else:
            db.session.add(IATraining(telephone_client="Admin", message_client=phrase_cle, mauvaise_reponse="Manuel", bonne_reponse=reponse_cle, corrige=True))
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "invalid_data"}), 400

if __name__ == '__main__':
    app.run(debug=True)