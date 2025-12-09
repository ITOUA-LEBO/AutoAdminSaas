import streamlit as st
import os
import pandas as pd
# On importe nos outils créés dans l'étape précédente
from utils import generate_invoice_pdf, call_ai, save_to_history, load_history

# --- CONFIGURATION DES PROMPTS (Cerveau de l'IA) ---
# Ce sont les instructions cachées données à l'IA pour définir sa personnalité
SYSTEM_EMAIL = "Tu es un assistant pour freelance. Rédige un email professionnel, poli, clair et empathique."
SYSTEM_LETTER = "Tu es un assistant administratif expert. Rédige un courrier formel respectant les standards français (en-tête, politesse)."
SYSTEM_SUMMARY = "Tu es un assistant de synthèse. Résume ce texte administratif : 1. Points clés, 2. Actions à faire (To-Do), 3. Dates/Montants importants."

# --- CONFIGURATION DE LA PAGE WEB ---
st.set_page_config(page_title="AutoAdmin", page_icon="📂", layout="wide")
st.title("📂 AutoAdmin - Assistant Freelance")

# --- BARRE LATÉRALE (MENU) ---
with st.sidebar:
    st.header("👤 Mes Infos")
    # Ces infos seront utilisées dans les PDF générés
    my_name = st.text_input("Mon Nom / Entreprise", "Jean Freelance")
    my_siret = st.text_input("Mon SIRET", "123 456 789 00010")

    st.divider()  # Une ligne de séparation visuelle

    # Le menu de navigation
    menu = st.radio(
        "Menu",
        ["Générateur Devis/Facture", "Assistant Email", "Courriers Admin", "Analyseur de Docs", "Historique",
         "Abonnement Pro"]
    )

# --- PAGE 1 : GÉNÉRATEUR ---
if menu == "Générateur Devis/Facture":
    st.subheader("💰 Créer un document comptable")

    # On divise l'écran en 2 colonnes
    col1, col2 = st.columns(2)

    with col1:
        doc_type = st.selectbox("Type de document", ["Devis", "Facture"])
        client_name = st.text_input("Nom du Client")
        client_address = st.text_input("Adresse Client")

    with col2:
        st.write("Détails de la prestation :")
        desc = st.text_area("Description prestation")
        price = st.number_input("Montant (€)", min_value=0.0, step=10.0)

    # Le bouton d'action
    if st.button("Générer le PDF"):
        if client_name and desc:
            # On prépare les données pour la fonction
            item = {"desc": desc, "price": price}

            # Appel de la fonction magique dans utils.py
            filename = generate_invoice_pdf(
                doc_type,
                {"name": my_name, "siret": my_siret},
                {"name": client_name, "address": client_address},
                [item],
                price
            )

            # Affichage du bouton de téléchargement
            with open(filename, "rb") as pdf_file:
                st.download_button(
                    label="📥 Télécharger le PDF",
                    data=pdf_file,
                    file_name=filename,
                    mime="application/pdf"
                )

            # On enregistre dans l'historique
            save_to_history(doc_type, client_name, f"Montant: {price}€")
            st.success("Document généré avec succès !")
        else:
            st.error("Merci de remplir le nom du client et la description.")

# --- PAGE 2 : EMAIL ---
elif menu == "Assistant Email":
    st.subheader("📧 Rédacteur d'Emails IA")
    email_type = st.selectbox("Type d'email", ["Relance paiement impayé", "Envoi de devis", "Prospection commerciale",
                                               "Réponse candidature"])
    context = st.text_area("Contexte (ex: Le client s'appelle Marc, retard de 10 jours...)")

    if st.button("Générer l'email"):
        # On construit le prompt pour l'IA
        prompt = f"Rédige un email de type '{email_type}'. Contexte : {context}. Signé : {my_name}"

        # On affiche un spinner pendant que l'IA réfléchit
        with st.spinner("L'IA rédige..."):
            response = call_ai(SYSTEM_EMAIL, prompt)

        st.text_area("Brouillon proposé :", value=response, height=300)
        save_to_history("Email", "IA Génération", f"Type: {email_type}")

# --- PAGE 3 : COURRIERS ---
elif menu == "Courriers Admin":
    st.subheader("📝 Générateur de Lettres Officielles")
    letter_type = st.selectbox("Type", ["Résiliation contrat", "Attestation sur l'honneur", "Demande de délai URSSAF",
                                        "Mise en demeure"])
    details = st.text_area("Détails nécessaires (Dates, références contrat...)")

    if st.button("Rédiger la lettre"):
        prompt = f"Rédige une lettre pour '{letter_type}'. Mes infos: {my_name}, SIRET {my_siret}. Détails : {details}"
        with st.spinner("Rédaction en cours..."):
            response = call_ai(SYSTEM_LETTER, prompt)
        st.text_area("Lettre générée :", value=response, height=400)
        save_to_history("Lettre", "Administration", f"Type: {letter_type}")

# --- PAGE 4 : ANALYSEUR ---
elif menu == "Analyseur de Docs":
    st.subheader("🔍 Comprendre le jargon administratif")
    st.info("Copiez-collez ici un texte compliqué (ex: email des impôts, CGV...)")
    raw_text = st.text_area("Texte à analyser")

    if st.button("Analyser et Résumer"):
        if raw_text:
            with st.spinner("Analyse en cours..."):
                response = call_ai(SYSTEM_SUMMARY, raw_text)
            st.success("Analyse terminée !")
            st.markdown(response)  # Markdown permet d'afficher du gras et des listes
        else:
            st.warning("Veuillez coller du texte d'abord.")

# --- PAGE 5 : HISTORIQUE ---
elif menu == "Historique":
    st.subheader("📜 Historique de vos documents")
    history = load_history()
    if history:
        # On inverse la liste pour voir les derniers en premier
        df = pd.DataFrame(history[::-1])
        st.dataframe(df, use_container_width=True)
    else:
        st.write("Aucun document généré pour le moment.")

# --- PAGE 6 : ABONNEMENT ---
elif menu == "Abonnement Pro":
    st.subheader("💎 Passez à la version PRO")
    st.write("Ce module permet de simuler l'intégration Stripe.")

    # Bouton HTML personnalisé pour ressembler à un vrai bouton de paiement
    STRIPE_LINK = "#"  # Tu mettras ton vrai lien Stripe ici plus tard

    st.markdown(f"""
    <div style="text-align: center; margin-top: 20px;">
        <p>Débloquez la génération illimitée et le stockage Cloud pour 9,99€/mois.</p>
        <a href="{STRIPE_LINK}" target="_blank">
            <button style="background-color:#635bff; color:white; padding:12px 24px; border:none; border-radius:5px; cursor:pointer; font-size:16px; font-weight:bold;">
                💳 S'abonner via Stripe
            </button>
        </a>
        <p style="font-size:12px; color:gray; margin-top:10px;">Paiement sécurisé</p>
    </div>
    """, unsafe_allow_html=True)