# scraper_wa_ngoie.py
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def scraper_site_wa_ngoie():
    url = "https://onrender.com"
    output_file = "connaissances_knowledge_scraper.json"
    
    print(f"🌐 Connexion et extraction de la plateforme : {url}...")
    
    # Simulation d'un navigateur pour éviter tout blocage réseau
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # 1. Envoi de la requête HTTP pour récupérer le code HTML
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ Échec de la connexion. Code HTTP : {response.status_code}")
            return
            
        # 2. Initialisation de BeautifulSoup pour analyser l'arbre HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 3. Extraction et nettoyage des données textuelles stratégiques
        titre_principal = soup.find("h1").text.strip() if soup.find("h1") else "Wa Ngoie Food"
        
        print(f"✅ Site localisé : {titre_principal}")
        
        # Collecte de tous les blocs de textes descriptifs importants
        blocs_textes = []
        
        # Récupération des titres h2, h3, h4 et de leurs paragraphes associés
        for tag in soup.find_all(['h2', 'h3', 'h4', 'p', 'strong']):
            texte_nettoye = " ".join(tag.text.split()) # Élimine les sauts de lignes et espaces doubles
            if len(texte_nettoye) > 10 and texte_nettoye not in blocs_textes:
                blocs_textes.append(texte_nettoye)
        
        # 4. Structuration de la connaissance pour le cerveau de ton IA
        base_connaissance = {
            "identite_plateforme": titre_principal,
            "url_source": url,
            "date_du_scraping": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "corpus_savant": blocs_textes
        }
        
        # Chargement ou création du fichier global de connaissances JSON
        donnees_globales = {}
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    donnees_globales = json.load(f)
            except json.JSONDecodeError:
                donnees_globales = {}
                
        # Injection de la structure sous une clé dédiée à ton restaurant
        donnees_globales["wa_ngoie_food_official_data"] = base_connaissance
        
        # 5. Écriture définitive du fichier JSON sur le disque dur
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(donnees_globales, f, indent=4, ensure_ascii=False)
            
        print(f"💾 Succès total ! Toutes les infos ont été stockées dans '{output_file}'.")
        print(f"🧠 Nombre d'éléments sémantiques assimilés : {len(blocs_textes)}")

    except Exception as e:
        print(f"❌ Une complication est survenue lors du scraping : {str(e)}")

if __name__ == "__main__":
    scraper_site_wa_ngoie()
