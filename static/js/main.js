// static/js/main.js
let currentConversationId = null;
let enAttenteAdresse = false; 

document.addEventListener("DOMContentLoaded", () => {
    const listContainer = document.getElementById("convList");
    if (listContainer) {
        chargerHistoriqueSidebar();
    }
});

/**
 * 1. Récupère et affiche les discussions passées (Style Liste de Sessions)
 */
function chargerHistoriqueSidebar() {
    fetch('/conversations')
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById("convList");
            if (!list) return;
            list.innerHTML = "";
            
            if (data.length === 0) {
                list.innerHTML = `<div style="font-size:12px; color:#747775; padding:10px; text-align:center;">Aucun historique</div>`;
                return;
            }

            data.forEach(c => {
                const div = document.createElement("div");
                div.className = `conv-item ${c.id === currentConversationId ? 'active' : ''}`;
                div.innerText = c.titre;
                div.onclick = () => basculerDiscussionExistante(c.id);
                list.appendChild(div);
            });
        });
}

/**
 * 2. Charge tous les messages d'une discussion sélectionnée
 */
function basculerDiscussionExistante(id) {
    currentConversationId = id;
    enAttenteAdresse = false;
    chargerHistoriqueSidebar();

    fetch(`/conversations/${id}/messages`)
        .then(res => res.json())
        .then(data => {
            const box = document.getElementById("chatbox");
            if (!box) return;
            box.innerHTML = "";
            
            data.forEach(m => {
                ajouterBulleGraphique(m.role, m.contenu, m.image_path, false); 
            });
            box.scrollTop = box.scrollHeight;
        });
}

/**
 * 3. Génère une nouvelle session en base de données via l'API Flask (Fix 405)
 */
function nouvelleConversation() {
    fetch('/conversations/nouvelle', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            currentConversationId = data.conversation_id;
            enAttenteAdresse = false;
            const box = document.getElementById("chatbox");
            if (box) {
                box.innerHTML = `
                    <div class="message-row model">
                        <div class="message-author">ABM AI</div>
                        <div>Mboté ! Nouvelle session ouverte pour votre commande Wa Ngoie Food. Citez les plats que vous désirez manger.</div>
                    </div>`;
            }
            annulerApercuPhoto();
            chargerHistoriqueSidebar();
        }
    });
}

/**
 * 4. Gestion de la miniature de l'image (Aperçu corrigé)
 */
function afficherApercuImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById("previewImg").src = e.target.result;
            document.getElementById("imagePreviewContainer").style.display = "block";
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Nettoyer l'aperçu de la photo
function annulerApercuPhoto() {
    const input = document.getElementById("imageInput");
    if (input) input.value = "";
    const container = document.getElementById("imagePreviewContainer");
    if (container) container.style.display = "none";
}

/**
 * 5. Moteur d'envoi principal du message avec support des comptes et de l'adresse
 */
function sendMessage() {
    const input = document.getElementById("userInput");
    const fileInput = document.getElementById("imageInput");
    const text = input.value.trim();
    
    if (!text && !fileInput.files[0]) return;
    let file = fileInput.files[0];
    
    // Affichage immédiat du message de l'utilisateur
    ajouterBulleGraphique('user', text, file ? URL.createObjectURL(file) : null, false);
    input.value = "";
    annulerApercuPhoto();

    const formData = new FormData();
    
    // Traitement de l'adresse de livraison
    if (enAttenteAdresse) {
        formData.append('adresse', text);
        formData.append('message', text);
        enAttenteAdresse = false;
    } else {
        formData.append('message', text);
    }

    if (currentConversationId) formData.append('conversation_id', currentConversationId);
    if (file) formData.append('image', file);

    fetch('/chat', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => {
        if (data.conversation_id) {
            currentConversationId = data.conversation_id;
            chargerHistoriqueSidebar();
        }
        if (data.demande_adresse) {
            enAttenteAdresse = true;
        }

        // Effet d'écriture progressive (Streaming text)
        ajouterBulleGraphique('model', data.reply, null, true, () => {
            // Affichage autonome des visuels des articles en fin de texte
            if (data.items && data.items.length > 0) {
                data.items.forEach(item => {
                    const htmlArticle = `
                        <div style="margin-top:10px; padding:12px; border:1px solid #d4af37; border-radius:10px; display:inline-block; background:rgba(30,30,32,0.6); text-align:center;">
                            <p style="margin:0 0 8px 0; font-weight:bold; font-size:13px; color:#fff;">${item.nom}</p>
                            <img src="${item.url}" style="width:130px; height:90px; object-fit:cover; border-radius:6px;">
                        </div>`;
                    ajouterBulleGraphique('model', htmlArticle, null, false);
                });
            }
        });
        
        // Synthèse vocale de l'assistant
        const cleanText = data.reply.replace(/<[^>]*>/g, '').replace(/\*/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'fr-FR';
        window.speechSynthesis.speak(utterance);
    });
}

/**
 * 6. CORRECTION COMPLÈTE : Génère les bulles et transforme le Markdown de l'URL en vrai lien bleu HTML cliquable
 */
function ajouterBulleGraphique(role, contenu, imgUrl, appliquerStreaming = false, callbackFin = null) {
    const box = document.getElementById("chatbox");
    if (!box) return;

    const row = document.createElement("div");
    row.className = `message-row ${role}`;
    
    const authorDiv = document.createElement("div");
    authorDiv.className = "message-author";
    authorDiv.innerText = role === 'user' ? 'Vous' : 'ABM AI';
    row.appendChild(authorDiv);

    const contentDiv = document.createElement("div");
    row.appendChild(contentDiv);

    if (imgUrl) {
        contentDiv.innerHTML = `<img src="${imgUrl}" class="chat-img"><br>`;
    }

    box.appendChild(row);
    box.scrollTop = box.scrollHeight;

    // Détection sémantique Regex : Transforme [Texte](Lien) en une balise <a> cliquable, stable et stylée en bleu
    let contenuFormate = contenu.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color: #38bdf8; font-weight: bold; text-decoration: underline; display: inline-block; margin-top: 5px;">$1</a>');

    if (appliquerStreaming && role === 'model') {
        const mots = contenuFormate.split(" ");
        let i = 0;
        contentDiv.innerHTML = ""; 
        const interval = setInterval(() => {
            if (i < mots.length) {
                contentDiv.innerHTML += mots[i] + " ";
                box.scrollTop = box.scrollHeight;
                i++;
            } else {
                clearInterval(interval);
                if (callbackFin) callbackFin();
            }
        }, 50);
    } else {
        contentDiv.innerHTML += `<div>${contenuFormate}</div>`;
        box.scrollTop = box.scrollHeight;
        if (callbackFin) callbackFin();
    }
}

/**
 * 7. Reconnaissance vocale autonome
 */
function startVoiceRecognition() {
    const btn = document.getElementById("micBtn");
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.lang = 'fr-FR';
    recognition.continuous = false;

    recognition.onstart = () => {
        btn.classList.add("mic-active");
        btn.innerText = "🛑 Traitement en cours...";
    };
    recognition.onerror = () => { btn.classList.remove("mic-active"); btn.innerText = "🎙️ Saisie Vocale Autonome"; };
    recognition.onend = () => { btn.classList.remove("mic-active"); btn.innerText = "🎙️ Saisie Vocale Autonome"; };
    recognition.onresult = (event) => {
        const transcription = event.results[0][0].transcript;
        const userInput = document.getElementById("userInput");
        if (userInput) {
            userInput.value = transcription;
            setTimeout(() => { sendMessage(); }, 500);
        }
    };
    recognition.start();
}

/**
 * 8. Relance d'alerte immédiate pour forcer le gérant Wa Ngoie via WhatsApp
 */
function forcerAlerteInsister(cmdId) {
    const numeroResto = "243831674115"; // Numéro officiel de Wa Ngoie Food
    
    // Création du message de relance
    const messageRelance = `Rappel Urgent ! Ma commande Wa Ngoie Food #${cmdId} est en attente depuis trop longtemps. Pouvez-vous forcer la cuisine ? Merci !`;
    
    // Encodage strict pour éviter les coupures et les bugs de domaine DNS
    const messageEncode = encodeURIComponent(messageRelance);
    
    // Génération du lien parfait avec le slash obligatoire après wa.me
    const lienWhatsAppResto = `https://wa.me/${numeroResto}?text=${messageEncode}`;
    
    // Ouverture instantanée de WhatsApp dans un nouvel onglet
    window.open(lienWhatsAppResto, '_blank');
}