from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import datetime

from config import Config
from model import db, User, Commande, Conversation, MessageHistory
from manager import WaNgoieAdminManager
from utils_ai import analyser_commande_phrase, generer_lien_whatsapp_direct, MENU_DATA

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Initialisation UNIQUE des extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Forcer la création automatique des tables SQL dans PostgreSQL sur Render
with app.app_context():
    db.create_all()

admin_manager = WaNgoieAdminManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- VITRINES ---
@app.route('/')
def home():
    return render_template('index.html', menu=MENU_DATA, page_class="bg-restaurant")

@app.route('/menu')
def menu():
    return render_template('menu.html', menu=MENU_DATA, page_class="bg-menu")

# --- AUTHENTIFICATION ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        is_student = request.form.get('is_student_isipa') == 'on'
        
        if not username or not phone or not password:
            return "Veuillez remplir tous les champs obligatoires.", 400
            
        user_exists = User.query.filter((User.username == username) | (User.phone == phone)).first()
        if user_exists:
            return "Ce nom d'utilisateur ou numéro WhatsApp est déjà enregistré.", 400
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, phone=phone, password=hashed_password, is_student_isipa=is_student)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        if username == 'admin':
            return redirect(url_for('liste_commandes'))
        return redirect(url_for('chat'))
        
    return render_template('register.html', page_class="bg-auth")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.username == 'admin':
                return redirect(url_for('liste_commandes'))
            return redirect(url_for('chat'))
        return "Identifiants invalides. Veuillez réessayer.", 401
    return render_template('login.html', page_class="bg-auth")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# --- CONVERSATIONS SESSIONS ---
@app.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    convs = Conversation.query.filter_by(user_id=current_user.id, est_supprime=False).order_by(Conversation.date_creation.desc()).all()
    return jsonify([{"id": c.id, "titre": c.titre} for c in convs])

@app.route('/conversations/<int:conv_id>/messages', methods=['GET'])
@login_required
def get_messages(conv_id):
    conv = Conversation.query.filter_by(id=conv_id, user_id=current_user.id).first_or_404()
    msgs = MessageHistory.query.filter_by(conversation_id=conv.id).order_by(MessageHistory.date_envoi.asc()).all()
    return jsonify([{"role": m.role, "contenu": m.contenu, "image_path": m.image_path} for m in msgs])

@app.route('/conversations/nouvelle', methods=['POST'])
@login_required
def nouvelle_conversation_api():
    nouvelle_conv = Conversation(user_id=current_user.id, titre="Nouvelle Discussion")
    db.session.add(nouvelle_conv)
    db.session.commit()
    return jsonify({"success": True, "conversation_id": nouvelle_conv.id})

# --- CHAT MULTIMODAL ABM AI ---
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'GET':
        commandes_client = Commande.query.filter_by(username=current_user.username).all()
        return render_template('chat.html', page_class="bg-chat", commandes=commandes_client)

    text_message = request.form.get('message', '').strip()
    conv_id = request.form.get('conversation_id')
    image_file = request.files.get('image')
    adresse_client = request.form.get('adresse', '').strip()

    if not text_message and not image_file:
        return jsonify({"reply": "Mboté ! Veuillez entrer un message ou joindre un visuel pour commencer.", "items": []})

    if not conv_id or conv_id == 'null' or conv_id == '':
        titre_extrait = text_message[:25] + "..." if len(text_message) > 25 else text_message or "Discussion"
        nueva_conv = Conversation(user_id=current_user.id, titre=titre_extrait)
        db.session.add(nueva_conv)
        db.session.commit()
        conv_id = nueva_conv.id
    else:
        conv_id = int(conv_id)

    image_path_saved = None
    if image_file:
        filename = f"upload_{conv_id}_{int(datetime.datetime.utcnow().timestamp())}.jpg"
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])
        image_path_saved = f"/static/uploads/{filename}"
        image_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    user_msg_db = MessageHistory(conversation_id=conv_id, role='user', contenu=text_message, image_path=image_path_saved)
    db.session.add(user_msg_db)
    db.session.commit()

    message_clean = text_message.lower()
    items_visuels = []

    if adresse_client or ("adresse" in message_clean and ("kintambo" in message_clean or len(message_clean) > 15)):
        adresse_finale = adresse_client if adresse_client else text_message.replace("mon adresse:", "").replace("adresse:", "").strip()
        dernier_msg = MessageHistory.query.filter_by(conversation_id=conv_id, role='user').order_by(MessageHistory.date_envoi.desc()).offset(1).first()
        phrase_recherche = dernier_msg.contenu if dernier_msg else text_message
        
        panier, total = analyser_commande_phrase(phrase_recherche, est_etudiant_isipa=current_user.is_student_isipa)
        if not panier:
            panier, total = analyser_commande_phrase(text_message, est_etudiant_isipa=current_user.is_student_isipa)

        if panier:
            nouvelle_cmd = Commande(
                username=current_user.username, phone=current_user.phone,
                adresse_livraison=adresse_finale, contenu=", ".join(panier),
                total_brut=total, total_final=total
            )
            db.session.add(nouvelle_cmd)
            db.session.commit()
            
            admin_manager.synchroniser_nouvelle_commande(
                cmd_id=nouvelle_cmd.id, username=current_user.username,
                phone=current_user.phone, plats=panier, total=total, adresse=adresse_finale
            )
            
            for plat in panier:
                img = current_app.config.get('MENU_IMAGES', {}).get(plat.lower().strip())
                if img:
                    items_visuels.append({
                        "nom": plat.capitalize(),
                        "url": url_for('static', filename=f'images/{img}')
                    })

            lien_wa = generer_lien_whatsapp_direct(panier, total)
            reply_text = f"🍔 **Commande validée avec succès !** \n\nLes plats : {', '.join(panier).upper()} ont été enregistrés avec un total de {total} FC. Votre livraison pour l'adresse '{adresse_finale}' est en cours de préparation dans nos cuisines. Cliquez ici pour finaliser les détails sur WhatsApp avec notre équipe : {lien_wa}"
            
            ai_msg_db = MessageHistory(conversation_id=conv_id, role='model', contenu=reply_text)
            db.session.add(ai_msg_db)
            db.session.commit()
            return jsonify({"reply": reply_text, "items": items_visuels, "conversation_id": conv_id})

    # --- ENTRAÎNEMENT CONNAISSANCES IA ---
    if any(m in message_clean for m in ["qui t'a créé", "créateur", "developpeur", "développeur", "ingénieur", "ingenieur", "conçu", "concu", "manassé", "manasse", "qui est abm", "abm"]):
        reply_text = "Je suis fier d'être une création exclusive de **Manassé ABM**, ingénieur en logiciel de talent."
    elif any(m in message_clean for m in ["qui es-tu", "tu es quoi", "ton identité", "identité", "ton rôle", "rôle"]):
        reply_text = "Je suis **ABM AI**, l'intelligence artificielle de pointe dédiée au restaurant Wa Ngoie Food..."
    else:
        panier, total = analyser_commande_phrase(text_message, est_etudiant_isipa=current_user.is_student_isipa)
        if panier:
            reply_text = f"C'est parfait ! J'ai bien détecté votre choix : {', '.join(panier).upper()}. Pour valider votre commande de {total} FC, donnez-moi simplement votre adresse précise pour la livraison ! 🛵"
            return jsonify({"reply": reply_text, "items": [], "demande_adresse": True, "conversation_id": conv_id})
        else:
            reply_text = "Mboté ! Je n'ai pas pu identifier les plats. Veuillez citer les articles de notre menu."
            admin_manager.loguer_incomprehension_ia(text_message)
            ai_msg_db = MessageHistory(conversation_id=conv_id, role='model', contenu=reply_text)
            db.session.add(ai_msg_db)
            db.session.commit()
            return jsonify({"reply": reply_text, "items": items_visuels, "conversation_id": conv_id})

# --- REQUÊTES LOGISTIQUES ADMIN ---
@app.route('/client/insister/<int:cmd_id>', methods=['POST'])
@login_required
def client_insister(cmd_id):
    cmd = Commande.query.filter_by(id=cmd_id, username=current_user.username).first_or_404()
    if cmd.statut == "En attente":
        cmd.statut = "Client Insiste !"
        db.session.commit()
    msg_relance = f"Rappel Urgent ! Ma commande Wa Ngoie Food #{cmd.id} est en attente."
    return jsonify({"success": True, "redirect_url": f"https://wa.me/{Config.TELEPHONE_OFFICIEL_WHATSAPP}?text={msg_relance.replace(' ', '%20')}"})

@app.route('/admin/dashboard')
@login_required
def liste_commandes():
    if current_user.username != 'admin': return "Accès interdit.", 403
    return render_template('admin.html', page_class="bg-restaurant")

@app.route('/admin/commandes', methods=['GET'])
@login_required
def admin_fetch_commandes():
    if current_user.username != 'admin': return jsonify([]), 403
    cmds = Commande.query.order_by(Commande.date_creation.desc()).all()
    out = []
    for c in cmds:
        out.append({
            "id": c.id, "username": c.username, "phone": c.phone,
            "adresse": c.adresse_livraison, "contenu": c.contenu,
            "total": c.total_final, "statut": c.statut,
            "date": c.date_creation.strftime("%d/%m/%Y %H:%M")
        })
    return jsonify(out)

if __name__ == '__main__':
    app.run(debug=True)