/**
 * 🎨 APPLICATION WA NGOIE FOOD - LOGIQUE JS FRONTEND CENTRALE (PROD 2026 - BLOCK-FIX)
 * Conçu, nettoyé et optimisé par l'expert en ingénierie logicielle Manassé ABM
 */

const NUMERO_ADMIN_WANGOIE = "243831674115";

let panierEnAttente = null;
let brutEnAttente = 0;
let finalEnAttente = 0;

function genererLienWhatsApp(messageText) {
    const messageEncode = encodeURIComponent(messageText);
    const estMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    return estMobile ? `whatsapp://send?phone=${NUMERO_ADMIN_WANGOIE}&text=${messageEncode}` : `https://whatsapp.com{NUMERO_ADMIN_WANGOIE}&text=${messageEncode}`;
}

function sendMessage() {
    const input = document.getElementById("userInput");
    if (!input) return;
    const message = input.value.trim();
    if (message === "") return;

    ajouterBulleGraphique("user", message, null, false);
    input.value = ""; 

    // On cache les boutons de choix dès que l'utilisateur renvoie un message
    document.getElementById("choice-container").style.display = "none";

    const box = document.getElementById("chatbox");
    const loaderRow = document.createElement("div");
    loaderRow.className = "message-row model temp-loader";
    loaderRow.innerHTML = `<div class="message-author">ABM AI</div><div class="content" style="color: #747775; font-style: italic;">En cours d'analyse sémantique...</div>`;
    box.appendChild(loaderRow);
    box.scrollTop = box.scrollHeight;

    const formData = new FormData();
    formData.append("message", message);

    fetch("/api/chat/message", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
        const loader = box.querySelector(".temp-loader");
        if (loader) loader.remove();

        if (data.status === "trigger_order" && panierEnAttente !== null) {
            ajouterBulleGraphique("model", data.response, null, false);
            executerEnregistrementCommande();
        } else {
            if (data.metadata) {
                panierEnAttente = data.metadata.contenu;
                brutEnAttente = data.metadata.brut;
                finalEnAttente = data.metadata.final;
                // Affiche le panier avec activation des boutons fixes natifs à la fin du streaming
                ajouterBulleGraphique("model", data.response, null, true, true);
            } else {
                ajouterBulleGraphique("model", data.response, null, true, false);
            }
        }
    })
    .catch(() => {
        const loader = box.querySelector(".temp-loader");
        if (loader) loader.remove();
        ajouterBulleGraphique("model", "Erreur technique de transmission réseau.", null, false);
    });
}

// Fonction déclenchée par les boutons fixes HTML
function validerChoixIA(reponse) {
    document.getElementById("choice-container").style.display = "none";
    if (reponse === 'oui') {
        ajouterBulleGraphique("user", "Oui", null, false);
        executerEnregistrementCommande();
    } else {
        ajouterBulleGraphique("user", "Non", null, false);
        ajouterBulleGraphique("model", "Commande annulée. Que désirez-vous d'autre ?", null, false);
        panierEnAttente = null;
    }
}

function executerEnregistrementCommande() {
    if (!panierEnAttente) return;
    
    const formData = new FormData();
    formData.append("contenu", panierEnAttente);
    formData.append("total_brut", brutEnAttente);
    formData.append("total_final", finalEnAttente);

    fetch("/api/commande/creer", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            const texteWhatsApp = `Mboté ! Je confirme ma commande officielle Wa Ngoie Food #${data.cmd_id} d'un montant de ${finalEnAttente.toLocaleString()} FC. Merci de lancer le Chef !`;
            panierEnAttente = null;
            window.open(genererLienWhatsApp(texteWhatsApp), '_blank');
            setTimeout(() => { window.location.reload(); }, 1000);
        }
    });
}

function ajouterBulleGraphique(role, contenu, imgUrl, appliquerStreaming = false, activerBoutonsChoix = false) {
    const box = document.getElementById("chatbox");
    if (!box) return;

    const row = document.createElement("div");
    row.className = `message-row ${role}`;
    row.innerHTML = `<div class="message-author">${role === 'user' ? 'Vous' : 'ABM AI'}</div><div class="content"></div>`;
    box.appendChild(row);
    const contentDiv = row.querySelector('.content');

    if (imgUrl) {
        contentDiv.innerHTML = `<img src="${imgUrl}" class="chat-img" style="max-width: 200px; border-radius: 8px; margin-bottom: 8px;"><br>`;
    }

    let texteA_Afficher = contenu ? contenu : "";

    if (appliquerStreaming && role === 'model') {
        let contenuFormate = texteA_Afficher.replace(/\n/g, "<br>");
        const fragments = contenuFormate.split(" ");
        let i = 0;
        
        const interval = setInterval(() => {
            if (i < fragments.length) {
                contentDiv.innerHTML += fragments[i] + " ";
                box.scrollTop = box.scrollHeight;
                i++;
            } else {
                clearInterval(interval);
                // Affiche de manière sécurisée les boutons de choix fixes en bas de la page
                if (activerBoutonsChoix) {
                    const container = document.getElementById("choice-container");
                    if (container) container.style.display = "flex";
                    box.scrollTop = box.scrollHeight;
                }
            }
        }, 20);
    } else {
        contentDiv.innerHTML += `<div>${texteA_Afficher.replace(/\n/g, "<br>")}</div>`;
        if (activerBoutonsChoix) {
            const container = document.getElementById("choice-container");
            if (container) container.style.display = "flex";
        }
        box.scrollTop = box.scrollHeight;
    }
}

function forcerAlerteInsister(cmdId) {
    if (!confirm("Signaler cette commande comme urgente au gérant ?")) return;
    fetch(`/api/commande/${cmdId}/insister`, { method: "POST" })
    .then(() => {
        window.open(genererLienWhatsApp(`Urgence Commande Wa Ngoie Food #${cmdId}`), '_blank');
        setTimeout(() => { window.location.reload(); }, 500);
    });
}

function afficherApercuImage(input) {
    const conteneur = document.getElementById("imagePreviewContainer");
    const image = document.getElementById("previewImg");
    if (input.files && input.files) {
        const reader = new FileReader();
        reader.onload = function(e) { image.src = e.target.result; conteneur.style.display = "block"; };
        reader.readAsDataURL(input.files);
    }
}

function annulerApercuPhoto() {
    const input = document.getElementById("imageInput");
    const conteneur = document.getElementById("imagePreviewContainer");
    if (input) input.value = "";
    if (conteneur) conteneur.style.display = "none";
}

function startVoiceRecognition() {
    const micBtn = document.getElementById("micBtn");
    const userInput = document.getElementById("userInput");
    if (!('webkitSpeechRecognition' in window) && !('speechRecognition' in window)) return;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = "fr-FR"; 
    micBtn.innerHTML = "⏳ Écoute...";
    recognition.start();
    recognition.onresult = function(event) {
        if (userInput && event.results.transcript) {
            userInput.value = event.results.transcript;
            sendMessage();
        }
    };
    recognition.onend = function() { micBtn.innerHTML = "🎙️ Vocale"; };
}
