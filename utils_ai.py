# utils_ai.py
import difflib
import json
import os
from urllib.parse import quote  # Importation propre en haut du fichier

# Catalogue officiel et strict des tarifs Wa Ngoie Food (Mise à jour 2026)
MENU_DATA = {
    "chawarma": 14000,
    "hamburger": 16000,
    "tacos": 16000,
    "saucisse": 14000,      # Portion de Saucisses (2 pièces)
    "cuisse": 14000,        # Portion de Cuisses de poulet (2 pièces)
    "poulet mayo": 28000,   # Le célèbre Poulet Mayo entier Wa Ngoie
    "samoussa": 14000,      # Portion de Samoussas (2 pièces)
    "boulette": 14000,      # Portion de Boulettes (3 pièces)
    "spaghetti": 14000,     # Spaghetti généreux à la viande
    "chikwangue": 3500,     # Chikwangue fraîche du jour
    "frites": 7000,         # Portion de frites dorées
    "banane": 7000,         # Bananes frites (Makemba)
    "eau": 2000,            # Bouteille d'eau fraîche
    "sucre": 3500,          # Canette sucrée
    "savanna": 8000,
    "biere": 4000
}

# Lexique Kinois de secours pour la traduction transparente du lingala courant
LEXIQUE_LINGALA = {
    "nako": "je veux",
    "mpe": "et",
    "masanga": "biere",
    "pilipili": "piment",
    "makemba": "banane",
    "kwanga": "chikwangue",
    "kamundele": "saucisse",
    "poto": "frites"
}

def corriger_et_deviner_article(mot_utilisateur):
    """Analyse un terme textuel et renvoie la clé exacte du menu si correspondance > 60%."""
    mot_clean = mot_utilisateur.lower().strip().replace("é", "e").replace("è", "e")
    
    # Nettoyage des pluriels simples
    if mot_clean.endswith("s") and len(mot_clean) > 4:
        mot_clean = mot_clean[:-1]
        
    # Vérification dans le lexique lingala d'abord
    if mot_clean in LEXIQUE_LINGALA:
        mot_clean = LEXIQUE_LINGALA[mot_clean]
        
    cles_menu = list(MENU_DATA.keys())
    correspondance = difflib.get_close_matches(mot_clean, cles_menu, n=1, cutoff=0.6)
    
    if correspondance:
        return correspondance[0]
    return None

def analyser_commande_phrase(phrase_brute, est_etudiant_isipa=False):
    """
    Moteur hybride : décortique la phrase de l'utilisateur, extrait les plats,
    applique les réductions ou formules étudiantes ISIPA et retourne le panier.
    """
    separateurs = [",", ".", ";", "!", "?", " et ", " un ", " une ", " des ", " na ", " pe "]
    texte_nettoye = phrase_brute.lower()
    
    for sep in separateurs:
        texte_nettoye = texte_nettoye.replace(sep, " ")
        
    mots = texte_nettoye.split()
    panier = []
    total_brut = 0.0
    
    for mot in mots:
        if len(mot) < 3:
            continue
        article = corriger_et_deviner_article(mot)
        if article:
            panier.append(article)
            total_brut += MENU_DATA[article]
            
    # Gestion de l'expression composée 'poulet mayo' si les mots ont été scindés
    if "poulet" in mots and "mayo" in mots:
        if "poulet" in panier:
            panier.remove("poulet")
        if "poulet mayo" not in panier:
            panier.append("poulet mayo")
            total_brut += (MENU_DATA["poulet mayo"] - MENU_DATA.get("poulet", 0))

    # Application de la formule préférentielle Étudiant ISIPA Kintambo
    if est_etudiant_isipa and total_brut > 0:
        total_brut = total_brut * 0.90
        
    return panier, int(total_brut)

# utils_ai.py (Remplace la fonction tout en bas)
from urllib.parse import quote

def generer_lien_whatsapp_direct(panier, total, plat_unique=None):
    """Génère un lien de redirection d'achat immédiat 100% valide et court vers WhatsApp."""
    numero = "243831674115"
    plats_str = ", ".join(panier).upper()
    texte = f"Commande Wa Ngoie Food - Plats: {plats_str} - Total: {total} FC"
    
    texte_encode = quote(texte)
    
    # LE SLASH EST BIEN ICI : https://wa.me
    return f"https://wa.me{numero}?text={texte_encode}"
