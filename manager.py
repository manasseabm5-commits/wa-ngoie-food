# manager.py
import json
import datetime
import os

class WaNgoieAdminManager:
    """Gestionnaire de persistance JSON adapté à l'environnement éphémère de Render."""
    def __init__(self):
        # Utilisation de /tmp garantit le droit d'écriture sur les serveurs Linux de Render
        self.base_path = '/tmp' if os.path.exists('/tmp') else '.'
        self.cmd_file = os.path.join(self.base_path, 'commandes_du_jour.json')
        self.corbeille_file = os.path.join(self.base_path, 'corbeille.json')
        self.logs_erreurs = os.path.join(self.base_path, 'erreurs_semantiques.json')
        self._init_files()

    def _init_files(self):
        for file in [self.cmd_file, self.corbeille_file, self.logs_erreurs]:
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump([], f)

    def synchroniser_nouvelle_commande(self, cmd_id, username, phone, plats, total, adresse):
        maintenant = datetime.datetime.now()
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        try:
            with open(self.cmd_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []
            
        nouvelle_cmd = {
            "id": cmd_id,
            "client": username,
            "whatsapp": phone,
            "plats": plats,
            "total": total,
            "frais_livraison": 0,
            "adresse": adresse,
            "heure": maintenant.strftime("%H:%M:%S"),
            "date": maintenant.strftime("%Y-%m-%d"),
            "jour": jours[maintenant.weekday()],
            "status": "En attente",
            "livreur": "Non assigné"
        }
        data.append(nouvelle_cmd)
        
        with open(self.cmd_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def loguer_incomprehension_ia(self, phrase_inconnue):
        try:
            with open(self.logs_erreurs, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logs = []
        
        if not any(l['input'] == phrase_inconnue for l in logs):
            logs.append({
                "input": phrase_inconnue,
                "reponse": "Non compris par l'IA",
                "date": str(datetime.datetime.now())
            })
            with open(self.logs_erreurs, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=4, ensure_ascii=False)
