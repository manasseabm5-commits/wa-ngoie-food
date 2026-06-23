/**
 * APPLICATION WA NGOIE FOOD - LOGIQUE FRONTEND CENTRALE
 * Fait à la main par Manassé ABM - Fix Affichage Menu & Sauts de Ligne
 */

var NUMERO_ADMIN = "243831674115";

// Variables globales pour stocker temporairement les calculs du panier
var panierEnAttente = null;
var brutEnAttente = 0;
var finalEnAttente = 0;

// Cette fonction génère le bon lien WhatsApp selon qu'on est sur mobile ou ordinateur
function creerLienWhatsApp(texteMessage) {
    var texteEncode = encodeURIComponent(texteMessage);
    var estSurMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (estSurMobile) {
        return "whatsapp://send?phone=" + NUMERO_ADMIN + "&text=" + texteEncode;
    } else {
        return "https://whatsapp.com" + NUMERO_ADMIN + "&text=" + texteEncode;
    }
}

// Fonction principale pour envoyer le message de l'utilisateur
function sendMessage() {
    var champSaisie = document.getElementById("userInput");
    if (!champSaisie) return;
    
    var messageText = champSaisie.value.trim();
    if (messageText === "") return;

    // On affiche le message de l'utilisateur dans le chat
    creerBulleMessage("user", messageText, null, false, false);
    champSaisie.value = ""; 

    // On cache les boutons d'action (Oui / Annuler) pendant l'envoi
    var boiteChoix = document.getElementById("choice-container");
    if (boiteChoix) {
        boiteChoix.className = "choice-box-hidden";
    }

    // Affichage d'un indicateur de chargement naturel
    var zoneChat = document.getElementById("chatbox");
    var ligneChargement = document.createElement("div");
    ligneChargement.className = "message-row model chargement-ia";
    ligneChargement.innerHTML = '<div class="message-author">ABM AI</div><div class="content">En cours d\'analyse...</div>';
    zoneChat.appendChild(ligneChargement);
    zoneChat.scrollTop = zoneChat.scrollHeight;

    var donneesFormulaire = new FormData();
    donneesFormulaire.append("message", messageText);

    // Envoi de la requête au serveur Flask
    fetch("/api/chat/message", { 
        method: "POST", 
        body: donneesFormulaire 
    })
    .then(function(reponse) {
        return reponse.json();
    })
    .then(function(data) {
        // Suppression du loader de chargement
        var loader = zoneChat.querySelector(".chargement-ia");
        if (loader) loader.remove();

        if (data.status === "trigger_order" && panierEnAttente !== null) {
            creerBulleMessage("model", data.response, null, false, false);
            enregistrerCommandeServeur();
        } else {
            if (data.metadata) {
                // L'IA a détecté un plat, on met le panier en attente
                panierEnAttente = data.metadata.contenu;
                brutEnAttente = data.metadata.brut;
                finalEnAttente = data.metadata.final;
                creerBulleMessage("model", data.response, null, true, true);
            } else {
                creerBulleMessage("model", data.response, null, true, false);
            }
        }
    })
    .catch(function() {
        var loader = zoneChat.querySelector(".chargement-ia");
        if (loader) loader.remove();
        creerBulleMessage("model", "Désolé, une petite erreur réseau est survenue.", null, false, false);
    });
}

// Fonction déclenchée lors d'un clic sur les gros boutons d'action (Oui / Annuler)
function validerChoixIA(reponseUtilisateur) {
    var boiteChoix = document.getElementById("choice-container");
    if (boiteChoix) {
        boiteChoix.className = "choice-box-hidden";
    }

    if (reponseUtilisateur === 'oui') {
        creerBulleMessage("user", "Oui", null, false, false);
        enregistrerCommandeServeur();
    } else {
        creerBulleMessage("user", "Non", null, false, false);
        creerBulleMessage("model", "Commande annulée. Que désirez-vous d'autre ?", null, false, false);
        panierEnAttente = null;
    }
}

// Enregistrement définitif dans la base de données PostgreSQL de Render
function enregistrerCommandeServeur() {
    if (!panierEnAttente) return;
    
    var donneesCommande = new FormData();
    donneesCommande.append("contenu", panierEnAttente);
    donneesCommande.append("total_brut", brutEnAttente);
    donneesCommande.append("total_final", finalEnAttente);

    fetch("/api/commande/creer", { 
        method: "POST", 
        body: donneesCommande 
    })
    .then(function(reponse) {
        return reponse.json();
    })
    .then(function(data) {
        if (data.status === "success") {
            var messageWhatsApp = "Mboté ! Je confirme ma commande Wa Ngoie Food #" + data.cmd_id + " pour un total de " + finalEnAttente.toLocaleString() + " FC. Merci !";
            panierEnAttente = null;
            
            // Ouverture immédiate de l'onglet WhatsApp officiel
            window.open(creerLienWhatsApp(messageWhatsApp), '_blank');
            
            setTimeout(function() { 
                window.location.reload(); 
            }, 1000);
        }
    });
}

// Fonction pour insérer graphiquement une bulle de texte dans l'écran de discussion
function creerBulleMessage(role, texte, lienImage, effetTexte, afficherBoutons) {
    var zoneChat = document.getElementById("chatbox");
    if (!zoneChat) return;

    var conteneurLigne = document.createElement("div");
    conteneurLigne.className = "message-row " + role;
    
    var auteur = (role === 'user') ? 'Vous' : 'ABM AI';
    conteneurLigne.innerHTML = '<div class="message-author">' + auteur + '</div><div class="content"></div>';
    zoneChat.appendChild(conteneurLigne);
    
    var zoneTexte = conteneurLigne.querySelector('.content');

    if (lienImage) {
        zoneTexte.innerHTML = '<img src="' + lienImage + '" class="chat-img"><br>';
    }

    var textePropre = texte ? texte : "";

    if (effetTexte && role === 'model') {
        // Remplacement correct des sauts de ligne pour préserver l'affichage aéré du menu
        var texteFormate = textePropre.replace(/\n/g, " <br> ");
        var fragments = texteFormate.split(" ");
        var compteur = 0;
        
        var minuterie = setInterval(function() {
            if (compteur < fragments.length) {
                if (fragments[compteur] === "<br>") {
                    zoneTexte.innerHTML += "<br>";
                } else {
                    zoneTexte.innerHTML += fragments[compteur] + " ";
                }
                zoneChat.scrollTop = zoneChat.scrollHeight;
                compteur++;
            } else {
                clearInterval(minuterie);
                if (afficherBoutons) {
                    var boutonsAction = document.getElementById("choice-container");
                    if (boutonsAction) boutonsAction.className = "choice-box-visible";
                    zoneChat.scrollTop = zoneChat.scrollHeight;
                }
            }
        }, 20);
    } else {
        zoneTexte.innerHTML += '<div>' + textePropre.replace(/\n/g, "<br>") + '</div>';
        if (afficherBoutons) {
            var boutonsAction = document.getElementById("choice-container");
            if (boutonsAction) boutonsAction.className = "choice-box-visible";
        }
        zoneChat.scrollTop = zoneChat.scrollHeight;
    }
}

// Fonction pour le bouton d'alerte rouge "🚨 Insister"
function forcerAlerteInsister(idCommande) {
    if (!confirm("Voulez-vous signaler au gérant que votre plat tarde ?")) return;
    
    fetch("/api/commande/" + idCommande + "/insister", { 
        method: "POST" 
    })
    .then(function() {
        var texteUrgence = "Urgence : Ma commande Wa Ngoie Food #" + idCommande + " prend du retard !";
        window.open(creerLienWhatsApp(texteUrgence), '_blank');
        setTimeout(function() { 
            window.location.reload(); 
        }, 500);
    });
}

// Gestion de l'aperçu de la photo (reçu ou preuve de paiement)
function afficherApercuImage(inputElement) {
    var boiteApercu = document.getElementById("imagePreviewContainer");
    var imageApercu = document.getElementById("previewImg");
    
    if (inputElement.files && inputElement.files[0]) {
        var lecteurFichier = new FileReader();
        lecteurFichier.onload = function(evenement) { 
            imageApercu.src = evenement.target.result; 
            boiteApercu.className = "preview-box-visible"; 
        };
        lecteurFichier.readAsDataURL(inputElement.files[0]);
    }
}

// Annuler la photo choisie
function annulerApercuPhoto() {
    var inputFichier = document.getElementById("imageInput");
    var boiteApercu = document.getElementById("imagePreviewContainer");
    
    if (inputFichier) inputFichier.value = "";
    if (boiteApercu) boiteApercu.className = "preview-box-hidden";
}

// Reconnaissance vocale par le micro du téléphone / ordinateur
function startVoiceRecognition() {
    var boutonMicro = document.getElementById("micBtn");
    var champTexte = document.getElementById("userInput");
    
    if (!('webkitSpeechRecognition' in window) && !('speechRecognition' in window)) {
        alert("La reconnaissance vocale n'est pas supportée par votre navigateur.");
        return;
    }
    
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var reconnaissance = new SpeechRecognition();
    reconnaissance.lang = "fr-FR"; 
    
    boutonMicro.innerHTML = "⏳ Écoute en cours...";
    reconnaissance.start();
    
    reconnaissance.onresult = function(evenement) {
        if (champTexte && evenement.results[0][0].transcript) {
            champTexte.value = evenement.results[0][0].transcript;
            sendMessage();
        }
    };
    
    reconnaissance.onend = function() { 
        boutonMicro.innerHTML = "🎙️ Parler au micro"; 
    };
}
