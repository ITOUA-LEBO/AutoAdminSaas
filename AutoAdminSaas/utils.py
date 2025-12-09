import os
import json
import openai
from fpdf import FPDF
from datetime import datetime
from dotenv import load_dotenv

# 1. On charge la clé de sécurité depuis le fichier .env
load_dotenv()

# 2. On connecte le client OpenAI
# Si tu n'as pas mis ta clé dans .env, ça plantera ici !
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Le fichier où sera stocké l'historique
DB_FILE = "data/documents.json"


# --- FONCTIONS POUR L'HISTORIQUE (JSON) ---
def load_history():
    """Lit le fichier JSON pour récupérer l'historique."""
    if not os.path.exists(DB_FILE):
        return []  # Si le fichier n'existe pas, on retourne une liste vide
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_to_history(doc_type, client_name, content_summary):
    """Ajoute une nouvelle entrée dans le fichier JSON."""
    history = load_history()
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": doc_type,
        "client": client_name,
        "summary": content_summary
    }
    history.append(entry)

    # Crée le dossier 'data' s'il n'existe pas encore
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

    with open(DB_FILE, "w") as f:
        json.dump(history, f, indent=4)


# --- FONCTION POUR GÉNÉRER LE PDF (DEVIS/FACTURE) ---
class PDF(FPDF):
    """Classe personnalisée pour le design du PDF"""

    def header(self):
        self.set_font('Arial', 'B', 15)
        # Titre centré en haut de chaque page
        self.cell(0, 10, 'AutoAdmin - Document', 0, 1, 'C')
        self.ln(10)  # Saut de ligne


def generate_invoice_pdf(doc_type, my_info, client_info, items, total):
    """
    Crée un fichier PDF avec les infos données.
    doc_type: 'Devis' ou 'Facture'
    my_info: Dictionnaire {name, siret}
    client_info: Dictionnaire {name, address}
    items: Liste de prestations
    total: Montant total
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Bloc Émetteur (Toi)
    pdf.cell(200, 10, txt=f"Emetteur : {my_info['name']}", ln=1)
    pdf.cell(200, 10, txt=f"SIRET : {my_info['siret']}", ln=1)
    pdf.ln(10)

    # Bloc Client
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Client : {client_info['name']}", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Adresse : {client_info['address']}", ln=1)
    pdf.ln(10)

    # Titre du Document (ex: Facture #202310...)
    pdf.set_font("Arial", 'B', 16)
    ref_number = datetime.now().strftime('%Y%m%d-%H%M')
    pdf.cell(200, 10, txt=f"{doc_type} #{ref_number}", ln=1, align='C')
    pdf.ln(10)

    # En-tête du tableau
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Description", 1)  # Colonne large
    pdf.cell(40, 10, "Prix", 1)  # Colonne prix
    pdf.ln()

    # Lignes du tableau (Prestations)
    pdf.set_font("Arial", size=12)
    for item in items:
        pdf.cell(140, 10, item['desc'], 1)
        pdf.cell(40, 10, f"{item['price']} EUR", 1)
        pdf.ln()

    pdf.ln(10)

    # Total
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"TOTAL A PAYER : {total} EUR", ln=1, align='R')

    # On sauvegarde le PDF avec un nom unique
    filename = f"{doc_type}_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
    pdf.output(filename)
    return filename


# --- FONCTION POUR PARLER À L'IA ---
def call_ai(system_prompt, user_prompt):
    """Envoie une requête à OpenAI et retourne le texte."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Modèle rapide et pas cher
            messages=[
                {"role": "system", "content": system_prompt},  # Les instructions secrètes (ton de voix)
                {"role": "user", "content": user_prompt}  # La demande de l'utilisateur
            ],
            temperature=0.7  # Créativité modérée
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur IA : {str(e)}"