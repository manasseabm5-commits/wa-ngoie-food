/**
 * 🎨 APPLICATION WA NGOIE FOOD - LOGIQUE JS FRONTEND CENTRALE (PROD 2026 - COMPLÈTE)
 * Conçu, nettoyé et optimisé par l'expert en ingénierie logicielle Manassé ABM
 */

const NUMERO_ADMIN_WANGOIE = "243831674115";

function genererLienWhatsApp(messageText) {
    const messageEncode = encodeURIComponent(messageText);
    const estMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    return estMobile ? `whatsapp://send?phone=${NUMERO_ADMIN_WANGOIE}&text=${messageEncode}` : `https://whatsapp.com{NUMERO_ADMIN_WANGOIE}&text=${messageEncode}`;
}

function sendMessage() {
    const input = document.getElementById("userInput");
    const imageInput = document.getElementById("imageInput");
    if (!input) return;
    
    const message = input.value.trim();
    const aUnePhoto = imageInput && imageInput.files && imageInput.files.length > 0;

    if (message === "" && !aUnePhoto) return;

    let imageLocaleUrl = null;
    if (aUnePhoto) {
        imageLocaleUrl = URL.createObjectURL(imageInput.files[0]);
    }

    ajouterBulleGraphique("user", message, imageLocaleUrl, false);
    input.value = ""; 
    annulerApercuPhoto();

    const box = document.getElementById("chatbox");
    const loaderRow = document.createElement("div");
    loaderRow.className = "message-row model temp-loader";
    loaderRow.innerHTML = `<div class="message-author">ABM AI</div><div class="content" style="color: #747775; font-style: italic;">En cours d'analyse sémantique...</div>`;
    box.appendChild(loaderRow);
    box.scrollTop = box.scrollHeight;

    const formData = new FormData();
    formData.append("message", message);
    if (aUnePhoto) {
        formData.append("imageInput", imageInput.files[0]);
    }

    fetch("/api/chat/message", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
        const loader = box.querySelector(".temp-loader");
        if (loader) loader.remove();
        if (data.status === "success") {
            ajouterBulleGraphique("model", data.response, null, true);
        }
    })
    .catch(() => {
        const loader = box.querySelector(".temp-loader");
        if (loader) loader.remove();
        ajouterBulleGraphique("model", "Erreur technique de transmission réseau.", null, false);
    });
}

function confirmerEtAjouterCommande(panierText, brut, final) {
    const formData = new FormData();
    formData.append("contenu", panierText);
    formData.append("total_brut", brut);
    formData.append("total_final", final);

    fetch("/api/commande/creer", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            const texteWhatsApp = `Mboté ! Je confirme ma commande officielle Wa Ngoie Food #${data.cmd_id} pour un montant de ${final.toLocaleString()} FC. Merci de lancer le Chef !`;
            window.open(genererLienWhatsApp(texteWhatsApp), '_blank');
            setTimeout(() => { location.reload(); }, 800);
        }
    });
}

function ajouterBulleGraphique(role, contenu, imgUrl, appliquerStreaming = false) {
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
                const btnAction = contentDiv.querySelector('.btn-trigger-confirm');
                if (btnAction) btnAction.style.display = "inline-block";
            }
        }, 20);
    } else {
        contentDiv.innerHTML += `<div>${texteA_Afficher.replace(/\n/g, "<br>")}</div>`;
        box.scrollTop = box.scrollHeight;
        const btnAction = contentDiv.querySelector('.btn-trigger-confirm');
        if (btnAction) btnAction.style.display = "inline-block";
    }
}

function forcerAlerteInsister(cmdId) {
    if (!confirm("Signaler cette commande comme urgente au gérant ?")) return;
    fetch(`/api/commande/${cmdId}/insister`, { method: "POST" })
    .then(() => {
        window.open(genererLienWhatsApp(`Urgence Commande Wa Ngoie Food #${cmdId}`), '_blank');
        location.reload();
    });
}

function afficherApercuImage(input) {
    const conteneur = document.getElementById("imagePreviewContainer");
    const image = document.getElementById("previewImg");
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) { image.src = e.target.result; conteneur.style.display = "block"; };
        reader.readAsDataURL(input.files[0]);
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
    
    if (!('webkitSpeechRecognition' in window) && !('speechRecognition' in window)) {
        alert("La reconnaissance vocale n'est pas supportée par votre navigateur actuel.");
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    // CORRECTIF SÉCURITÉ : Instanciation propre de l'API native [index]
    const recognition = new SpeechRecognition();
    
    recognition.lang = "fr-FR"; 
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    
    micBtn.innerHTML = "⏳ Écoute...";
    micBtn.style.borderColor = "#25d366";
    micBtn.style.color = "#25d366";
    
    recognition.start();
    
    recognition.onresult = function(event) {
        const texteFormule = event.results[0][0].transcript;
        if (userInput && texteFormule) {
            userInput.value = texteFormule;
            sendMessage();
        }
    };
    
    recognition.onerror = function() { micBtn.innerHTML = "🎙️ Vocale"; };
    recognition.onend = function() {
        micBtn.innerHTML = "🎙️ Vocale";
        micBtn.style.borderColor = "#2f2f32";
        micBtn.style.color = "#c4c7c5";
    };
}
