# manager.py
import json
import datetime
import os

class WaNgoieAdminManager:
    """Gestionnaire de persistance JSON pour les flux logistiques journaliers de l'administration."""
    def __init__(self):
        self.cmd_file = 'commandes_du_jour.json'
        self.corbeille_file = 'corbeille.json'
        self.logs_erreurs = 'erreurs_semantiques.json'
        self._init_files()

    def _init_files(self):
        for file in [self.cmd_file, self.corbeille_file, self.logs_erreurs]:
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump([], f)

    def synchroniser_nouvelle_commande(self, cmd_id, username, phone, plats, total, adresse):
        """Injecte une commande active en arrière-plan dans le JSON d'audit de l'administrateur."""
        maintenant = datetime.datetime.now()
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        with open(self.cmd_file, 'r+', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
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
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4, ensure_ascii=False)

    def loguer_incomprehension_ia(self, phrase_inconnue):
        """Enregistre les phrases non assimilées par ABM AI pour affichage dans le hub de formation."""
        with open(self.logs_erreurs, 'r+', encoding='utf-8') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
            
            # Éviter de surcharger avec la même phrase exacte
            if not any(l['input'] == phrase_inconnue for l in logs):
                logs.append({
                    "input": phrase_inconnue,
                    "reponse": "Non compris par l'IA",
                    "date": str(datetime.datetime.now())
                })
                f.seek(0)
                f.truncate()
                json.dump(logs, f, indent=4, ensure_ascii=False)
