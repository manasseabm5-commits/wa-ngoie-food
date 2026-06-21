/**
 * 🎨 APPLICATION WA NGOIE FOOD - LOGIQUE JS FRONTEND CENTRALE (PROD 2026)
 * Conçu et optimisé par l'expert en ingénierie logicielle Manassé ABM
 */

const NUMERO_ADMIN_WANGOIE = "243831674115";

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
        if (data.status === "success") {
            ajouterBulleGraphique("model", data.response, null, true);
        }
    })
    .catch(() => {
        const loader = box.querySelector(".temp-loader");
        if (loader) loader.remove();
        ajouterBulleGraphique("model", "Erreur de connexion internet.", null, false);
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
            const texteWhatsApp = `Mboté ! Je confirme ma commande officielle Wa Ngoie Food #${data.cmd_id} d'un montant de ${final} FC. Merci de lancer la cuisine !`;
            window.open(genererLienWhatsApp(texteWhatsApp), '_blank');
            setTimeout(() => { location.reload(); }, 1000);
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

    if (appliquerStreaming && role === 'model') {
        let contenuFormate = contenu.replace(/\n/g, "<br>");
        const fragments = contenuFormate.split(" ");
        let i = 0;
        const interval = setInterval(() => {
            if (i < fragments.length) {
                contentDiv.innerHTML += fragments[i] + " ";
                box.scrollTop = box.scrollHeight;
                i++;
            } else {
                clearInterval(interval);
                // Si l'IA a injecté un bouton invisible de confirmation, on l'active
                const btnAction = contentDiv.querySelector('.btn-trigger-confirm');
                if (btnAction) btnAction.style.display = "inline-block";
            }
        }, 20);
    } else {
        contentDiv.innerHTML = `<div>${contenu}</div>`;
        box.scrollTop = box.scrollHeight;
    }
}

function forcerAlerteInsister(cmdId) {
    if (!confirm("Signaler cette commande comme urgente ?")) return;
    fetch(`/api/commande/${cmdId}/insister`, { method: "POST" })
    .then(() => {
        window.open(genererLienWhatsApp(`Urgence Commande Wa Ngoie Food #${cmdId}`), '_blank');
        location.reload();
    });
}
