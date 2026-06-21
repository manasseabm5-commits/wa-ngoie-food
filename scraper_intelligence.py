import requests
from bs4 import BeautifulSoup
import json

# URL de votre plateforme marchande
URL = "https://onrender.com"

def scraper_page_ia(url):
    try:
        # 1. Envoi de la requête HTTP
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # 2. Analyse du code HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Supprimer les balises inutiles pour l'entraînement d'une IA (scripts, styles)
        for element in soup(["script", "style", "nav", "footer"]):
            element.extract()
            
        connaissances = []
        
        # 3. Extraction structurée (Titres et paragraphes associés)
        # On parcourt les éléments clés du flux de la page
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
            texte_propre = tag.get_text(strip=True)
            if texte_propre:
                connaissances.append({
                    "balise": tag.name,
                    "contenu": texte_propre
                })
                
        # 4. Sauvegarde des données propres au format JSON pour l'IA
        with open("donnees_wa_ngoie_food.json", "w", encoding="utf-8") as f:
            json.dump(connaissances, f, ensure_ascii=False, indent=4)
            
        print("Scraping réussi ! Fichier 'donnees_wa_ngoie_food.json' créé.")
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de la page : {e}")

# Lancement du scraper
if __name__ == "__main__":
    scraper_page_ia(URL)
