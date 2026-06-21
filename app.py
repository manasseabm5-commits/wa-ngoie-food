# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import json
import datetime

from config import Config
from model import db, User, Commande, Conversation, MessageHistory
from manager import WaNgoieAdminManager
from utils_ai import analyser_commande_phrase, generer_lien_whatsapp_direct, MENU_DATA

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Initialisation des extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Gestionnaire d'administration
admin_manager = WaNgoieAdminManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- VITRINES DE BASE ---
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
            
        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(username=username, phone=phone, password=hashed_password, is_student_isipa=is_student)
        db.session.add(new_user)
        db.session.commit()
        
        if username == 'admin':
            login_user(new_user)
            return redirect(url_for('liste_commandes'))
            
        login_user(new_user)
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

# --- HISTORIQUE & CONVERSATIONS SESSIONS ---
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

# --- CONSOLE DU CHAT MULTIMODAL ABM AI ---
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

    # --- ÉTAPE 1 : INTERCEPTION DE L'ADRESSE ---
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

    # --- ÉTAPE 2 : MOTEUR DE CONNAISSANCES ET COMPRÉHENSION ÉLITE ---
    if any(m in message_clean for m in ["qui t'a créé", "créateur", "developpeur", "développeur", "ingénieur", "ingenieur", "conçu", "concu", "manassé", "manasse", "qui est abm", "abm"]):
        reply_text = "Je suis fier d'être une création exclusive de **Manassé ABM**, ingénieur en logiciel de talent. Manassé a conçu toute mon architecture, mon cerveau logique et ma capacité à traiter vos commandes pour Wa Ngoie Food. Il est l'expert qui transforme la technologie en une expérience culinaire fluide. Grâce à ses compétences, je ne suis pas juste un programme, je suis votre partenaire privilégié pour manger sain et rapide à Kinshasa ! 🧠🚀✨"
    
    elif any(m in message_clean for m in ["qui es-tu", "tu es quoi", "ton identité", "identité", "ton rôle", "rôle", "assistant", "robot", "ia", "intelligence"]):
        reply_text = "Je suis **ABM AI**, l'intelligence artificielle de pointe dédiée au restaurant Wa Ngoie Food. Mon rôle est de vous offrir une expérience client de classe mondiale : je gère vos commandes, je calcule vos réductions étudiantes (ISIPA), et je vous apporte toutes les informations sur nos spécialités et notre localisation à Kintambo. Je suis là pour vous faire gagner du temps et vous assurer un service impeccable à chaque interaction ! 🤖🥪🔥"
    
    elif any(m in message_clean for m in ["où", "localisation", "adresse", "situé", "avenue oua", "komoriko", "isipa", "repere", "référence", "kinshasa", "kintambo"]):
        reply_text = "Wa Ngoie Food est situé au cœur de Kintambo, au numéro 14 de l'Avenue OUA, juste au croisement de la rue Komoriko. Notre point de repère principal est l'Université ISIPA, ce qui nous rend très accessibles. Que vous soyez un étudiant de l'ISIPA ou un habitant du quartier, vous êtes toujours les bienvenus chez nous pour découvrir nos recettes uniques ! 📍🏢"
    
    elif any(m in message_clean for m in ["heure", "horaire", "ouvert", "fermé", "ferme", "temps", "ouvrir", "fermer", "dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]):
        reply_text = "Nous sommes à votre service pour vous régaler tous les jours de la semaine, sauf le lundi. Nous sommes ouverts du mardi au dimanche, sans interruption, de **10h00 du matin jusqu'à 21h00**. C'est le moment idéal pour savourer nos plats, que ce soit pour une pause déjeuner ou un dîner savoureux avant 21h00 ! 🕒🥗"
    
    elif any(m in message_clean for m in ["manger sur place", "place", "assise", "espace", "table", "cadre", "resto"]):
        reply_text = "Oui, absolument ! Nous avons aménagé un cadre moderne, propre et très convivial au n°14 Avenue OUA à Kintambo pour ceux qui souhaitent manger sur place. Vous pouvez profiter de notre ambiance relaxante et savourer vos plats fraîchement préparés. Si vous êtes pressés, vous pouvez aussi commander ici pour une livraison rapide ! 🪑🍔✨"
    
    elif any(m in message_clean for m in ["bonjour", "salut", "mbote", "mboté", "hello", "hi", "hey", "bjr", "matondo", "merci"]):
        reply_text = "Mboté sango nini ! 👋 Bienvenue chez Wa Ngoie Food. Je suis votre assistant ABM AI, prêt à vous servir avec le sourire. Que puis-je vous préparer de bon aujourd'hui ? Que ce soit pour un chawarma, des frites ou toute autre spécialité de notre menu, je suis à votre écoute pour organiser votre festin ! 🥙🍟🥤"
    
    # --- ÉTAPE 3 : ANALYSE TRADITIONNELLE ---
    else:
        sujets_resto = ["menu", "carte", "prix", "chawarma", "hamburger", "tacos", "saucisse", "cuisse", "poulet", "samoussa", "boulette", "spaghetti", "chikwangue", "frites", "banane", "eau", "sucre", "savanna", "biere", "commander", "livrer", "manger", "faim", "gout", "repas", "spécialité"]
        
        if not any(keyword in message_clean for keyword in sujets_resto) and len(message_clean) > 8:
            reply_text = "C'est une réflexion très intéressante ! Toutefois, en tant qu'assistant de Wa Ngoie Food, ma mission est de vous aider à découvrir notre carte et à commander vos repas. Puis-je vous aider à choisir parmi nos meilleures spécialités aujourd'hui ? 🍔✨"
            ai_msg_db = MessageHistory(conversation_id=conv_id, role='model', contenu=reply_text)
            db.session.add(ai_msg_db)
            db.session.commit()
            return jsonify({"reply": reply_text, "items": [], "conversation_id": conv_id})

        if any(m in message_clean for m in ["menu", "carte", "afficher", "repas"]):
            reply_text = "Voici notre vitrine de délices ! Pour explorer tous nos produits, les tarifs détaillés et voir nos photos alléchantes, je vous invite à cliquer sur l'onglet 'Menu & Tarifs' en haut de votre écran. Vous y trouverez certainement votre bonheur culinaire ! 🍕🥗"
        else:
            panier, total = analyser_commande_phrase(text_message, est_etudiant_isipa=current_user.is_student_isipa)
            if panier:
                reply_text = f"C'est parfait ! J'ai bien détecté votre choix : {', '.join(panier).upper()}. Pour valider votre commande de {total} FC, donnez-moi simplement votre adresse précise pour la livraison ! 🛵"
                return jsonify({"reply": reply_text, "items": [], "demande_adresse": True, "conversation_id": conv_id})
            else:
                reply_text = "Mboté ! Je n'ai pas pu identifier les plats dans votre message. Veuillez citer les articles de notre menu pour que je puisse préparer votre commande sans erreur. Je suis à votre écoute ! 🍔"
                admin_manager.loguer_incomprehension_ia(text_message)
    
    ai_msg_db = MessageHistory(conversation_id=conv_id, role='model', contenu=reply_text)
    db.session.add(ai_msg_db)
    db.session.commit()
    return jsonify({"reply": reply_text, "items": items_visuels, "conversation_id": conv_id})

# --- CLIENT ACTIONS & ADMIN ---
# app.py (Remplace la route client_insister par celle-ci)
@app.route('/client/insister/<int:cmd_id>', methods=['POST'])
@login_required
def client_insister(cmd_id):
    cmd = Commande.query.filter_by(id=cmd_id, username=current_user.username).first_or_404()
    
    # On change temporairement le statut pour déclencher l'alarme chez l'admin
    if cmd.statut == "En attente":
        cmd.statut = "Client Insiste !"
        db.session.commit()
        
    msg_relance = f"Rappel Urgent ! Ma commande Wa Ngoie Food #{cmd.id} est en attente depuis trop longtemps."
    texte_encode = msg_relance.replace(" ", "%20")
    lien_lien = f"https://wa.me{Config.TELEPHONE_OFFICIEL_WHATSAPP}?text={texte_encode}"
    return jsonify({"success": True, "redirect_url": lien_lien})


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
        out.append({"id": c.id, "username": c.username, "phone": c.phone, "adresse": c.adresse_livraison,
                    "plats": c.contenu.split(", "), "total": c.total_brut, "frais_livraison": c.frais_livraison,
                    "total_final": c.total_final, "status": c.statut, "livreur": c.livreur_assigne or "Non assigné",
                    "heure": c.date_creation.strftime("%H:%M"), "date": c.date_creation.strftime("%d/%m/%Y")})
    return jsonify(out)

@app.route('/admin/commandes/<int:cmd_id>/action', methods=['POST'])
@login_required
def admin_action_commande(cmd_id):
    if current_user.username != 'admin': return jsonify({"success": False}), 403
    cmd = Commande.query.get_or_404(cmd_id)
    req_data = request.get_json() or {}
    action = req_data.get('action')
    if action == 'mettre_a_jour':
        cmd.frais_livraison = float(req_data.get('frais', 0.0))
        cmd.total_final = cmd.total_brut + cmd.frais_livraison
        cmd.statut = req_data.get('statut', 'En attente')
        cmd.livreur_assigne = req_data.get('livreur', 'Non assigné')
        db.session.commit()
        return jsonify({"success": True})
    elif action == 'supprimer':
        db.session.delete(cmd)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route('/admin/get-errors', methods=['GET'])
@login_required
def admin_get_errors():
    if current_user.username != 'admin': return jsonify([]), 403
    if os.path.exists('erreurs_semantiques.json'):
        with open('erreurs_semantiques.json', 'r', encoding='utf-8') as f:
            return f.read()
    return jsonify([])

@app.route('/admin/train-ia', methods=['POST'])
@login_required
def admin_train_ia():
    if current_user.username != 'admin': return jsonify({"success": False}), 403
    req_data = request.get_json() or {}
    if req_data.get('input') and req_data.get('reply'):
        file_path = 'connaissances.json'
        if os.path.exists(file_path):
            with open(file_path, 'r+', encoding='utf-8') as f:
                try: data = json.load(f)
                except: data = []
                data.append({"id": len(data) + 1, "input": req_data['input'].lower(), "intention": "APPRENTISSAGE", "reponse": req_data['reply']})
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4, ensure_ascii=False)
            return jsonify({"success": True})
    return jsonify({"success": False}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)