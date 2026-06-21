import requests
from bs4 import BeautifulSoup
import time

def scraper_wiktionnaire(mot):
    url = f"https://fr.wiktionary.org/wiki/{mot}"
    headers = {'User-Agent': 'MonAppLinguistique/1.0'}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Le contenu principal est souvent dans une div avec l'id 'mw-content-text'
    # Les définitions sont généralement dans des listes <li> après des titres <h3>
    contenu = soup.find('div', class_='mw-parser-output')
    
    resultats = []
    # On cherche les paragraphes qui suivent généralement les titres de sections
    for p in contenu.find_all('p'):
        texte = p.get_text(strip=True)
        if texte:
            resultats.append(texte)
            
    return resultats[:3]  # Retourne les 3 premières lignes de définition

# Test
mot_cherche = "chat"
print(scraper_wiktionnaire(mot_cherche))