# utils_ai.py
import difflib
# Utilisation de quote_plus pour garantir un encodage strict des espaces et caractères spéciaux
from urllib.parse import quote_plus

MENU_DATA = {
    "chawarma": 14000, "hamburger": 16000, "tacos": 16000,
    "saucisse": 14000, "cuisse": 14000, "poulet mayo": 28000,
    "samoussa": 14000, "boulette": 14000, "spaghetti": 14000,
    "chikwangue": 3500, "frites": 7000, "banane": 7000,
    "eau": 2000, "sucre": 3500, "savanna": 8000, "biere": 4000
}

LEXIQUE_LINGALA = {
    "nako": "je veux", "mpe": "et", "masanga": "biere", "pilipili": "piment",
    "makemba": "banane", "kwanga": "chikwangue", "kamundele": "saucisse", "poto": "frites"
}

def corriger_et_deviner_article(mot_utilisateur):
    mot_clean = mot_utilisateur.lower().strip().replace("é", "e").replace("è", "e")
    if mot_clean.endswith("s") and len(mot_clean) > 4:
        mot_clean = mot_clean[:-1]
    if mot_clean in LEXIQUE_LINGALA:
        mot_clean = LEXIQUE_LINGALA[mot_clean]
        
    cles_menu = list(MENU_DATA.keys())
    correspondance = difflib.get_close_matches(mot_clean, cles_menu, n=1, cutoff=0.6)
    # Sécurité pour éviter un crash 'IndexError' si aucune correspondance n'est trouvée
    return correspondance[0] if correspondance else None

def analyser_commande_phrase(phrase_brute, est_etudiant_isipa=False):
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
            
    if "poulet" in mots and "mayo" in mots:
        if "poulet" in panier:
            panier.remove("poulet")
        if "poulet mayo" not in panier:
            panier.append("poulet mayo")
            total_brut += (MENU_DATA["poulet mayo"] - MENU_DATA.get("poulet", 0))

    if est_etudiant_isipa and total_brut > 0:
        total_brut = total_brut * 0.90
        
    return panier, int(total_brut)

def generer_lien_whatsapp_direct(panier, total, plat_unique=None):
    numero = "243831674115"
    plats_str = ", ".join(panier).upper()
    texte = f"Commande Wa Ngoie Food - Plats: {plats_str} - Total: {total} FC"
    
    # Encodage parfait du texte pour WhatsApp sans perte de caractères
    texte_encode = quote_plus(texte)
    
    # Ajout du slash indispensable '/' pour former une URL valide https://wa.me
    return f"https://wa.me{numero}?text={texte_encode}"
