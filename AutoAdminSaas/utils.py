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

from fpdf import FPDF
from datetime import datetime
import math

class DocumentGenerator(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        
    def draw_star(self, x, y, size):
        """Dessine une étoile décorative"""
        self.set_line_width(2)
        self.set_draw_color(0, 0, 0)
        
        points = []
        for i in range(10):
            angle = math.pi * 2 * i / 10 - math.pi / 2
            r = size if i % 2 == 0 else size * 0.4
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            points.append((px, py))
        
        # Dessiner l'étoile
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]
            self.line(x1, y1, x2, y2)
    
    def rounded_rect(self, x, y, w, h, r):
        """Dessine un rectangle avec coins arrondis"""
        self.set_line_width(2)
        k = self.k
        hp = self.h
        
        # Convertir les coordonnées
        x, y, w, h, r = x * k, (hp - y) * k, w * k, -h * k, r * k
        
        # Dessiner le rectangle arrondi
        self.set_draw_color(0, 0, 0)
        op = 'S'  # Stroke only
        myArc = 4 / 3 * (math.sqrt(2) - 1)
        
        self._out(f'{(x + r):.2f} {(y):.2f} m')
        xc = x + w - r
        yc = y
        self._out(f'{(xc):.2f} {(yc):.2f} l')
        self._arc(xc + r * myArc, yc, xc + r, yc - r * myArc, xc + r, yc - r)
        xc = x + w
        yc = y - h + r
        self._out(f'{(xc):.2f} {(yc):.2f} l')
        self._arc(xc, yc - r * myArc, xc - r * myArc, yc - r, xc - r, yc - r)
        xc = x + r
        yc = y - h
        self._out(f'{(xc):.2f} {(yc):.2f} l')
        self._arc(xc - r * myArc, yc, xc - r, yc + r * myArc, xc - r, yc + r)
        xc = x
        yc = y - r
        self._out(f'{(xc):.2f} {(yc):.2f} l')
        self._arc(xc, yc + r * myArc, xc + r * myArc, yc + r, xc + r, yc + r)
        self._out(op)
    
    def _arc(self, x1, y1, x2, y2, x3, y3):
        """Helper pour dessiner un arc"""
        h = self.h
        self._out(f'{x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f} {x3:.2f} {y3:.2f} c')
    
    def create_document(self, doc_type, document_data):
        """
        Crée un document élégant (Facture ou Devis)
        
        Args:
            doc_type: 'Facture' ou 'Devis'
            document_data: dictionnaire avec les données
        """
        
        # Marges
        margin = 20
        page_width = 210  # A4 width in mm
        
        # En-tête "FACTURE" ou "DEVIS"
        self.set_font('Arial', 'B', 48)
        self.set_xy(margin, 25)
        self.cell(0, 20, doc_type.upper(), 0, 1)
        
        # Badge étoile décoratif
        self.draw_star(185, 30, 5)
        
        # Badges avec numéro et date
        y_badge = 50
        
        # Badge numéro
        self.rounded_rect(margin, y_badge, 50, 10, 3)
        self.set_font('Arial', '', 9)
        self.set_xy(margin + 2, y_badge + 2.5)
        self.cell(46, 5, f"{doc_type} n {document_data['number']}", 0, 0, 'L')
        
        # Badge date
        self.rounded_rect(margin + 55, y_badge, 35, 10, 3)
        self.set_xy(margin + 57, y_badge + 2.5)
        self.cell(31, 5, document_data['date'], 0, 0, 'L')
        
        # Ligne de séparation
        self.set_line_width(0.5)
        self.line(margin, 65, page_width - margin, 65)
        
        # Informations émetteur (gauche)
        y_info = 75
        self.set_font('Arial', 'B', 11)
        self.set_xy(margin, y_info)
        self.cell(0, 6, document_data['my_name'], 0, 1)
        
        self.set_font('Arial', '', 9)
        
        # SIRET si présent
        if 'my_siret' in document_data and document_data['my_siret']:
            self.set_x(margin)
            self.cell(0, 5, f"SIRET : {document_data['my_siret']}", 0, 1)
        
        self.set_x(margin)
        self.cell(0, 5, document_data['my_phone'], 0, 1)
        self.set_x(margin)
        self.cell(0, 5, document_data['my_email'], 0, 1)
        if 'my_website' in document_data:
            self.set_x(margin)
            self.cell(0, 5, document_data['my_website'], 0, 1)
        self.set_x(margin)
        self.cell(0, 5, document_data['my_address'], 0, 1)
        
        # Informations client (droite)
        self.set_font('Arial', 'B', 11)
        self.set_xy(120, y_info)
        self.cell(0, 6, "A L'ATTENTION DE", 0, 1, 'R')
        
        self.set_font('Arial', 'B', 10)
        self.set_xy(120, y_info + 6)
        self.cell(0, 5, document_data['client_name'], 0, 1, 'R')
        
        self.set_font('Arial', '', 9)
        self.set_xy(120, y_info + 11)
        self.cell(0, 5, document_data['client_phone'], 0, 1, 'R')
        self.set_xy(120, y_info + 16)
        self.cell(0, 5, document_data['client_address'], 0, 1, 'R')
        
        # Tableau des prestations
        y_table = 120
        self.set_xy(margin, y_table)
        
        # En-tête du tableau (fond noir)
        self.set_fill_color(0, 0, 0)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 10)
        
        col_widths = [90, 30, 30, 20]
        self.cell(col_widths[0], 8, 'DESCRIPTION', 1, 0, 'L', True)
        self.cell(col_widths[1], 8, 'PRIX', 1, 0, 'C', True)
        self.cell(col_widths[2], 8, 'QUANTITE', 1, 0, 'C', True)
        self.cell(col_widths[3], 8, 'TOTAL', 1, 1, 'R', True)
        
        # Corps du tableau
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 9)
        
        for item in document_data['items']:
            self.set_x(margin)
            self.cell(col_widths[0], 8, item['description'][:40], 1, 0, 'L')
            self.cell(col_widths[1], 8, f"{item['price']} EU", 1, 0, 'C')
            self.cell(col_widths[2], 8, f"{item['quantity']:02d}", 1, 0, 'C')
            self.cell(col_widths[3], 8, f"{item['price'] * item['quantity']} EU", 1, 1, 'R')
        
        # Calculs
        subtotal = sum(item['price'] * item['quantity'] for item in document_data['items'])
        tva_amount = subtotal * document_data['tva'] / 100
        total = subtotal + tva_amount
        
        # Bloc totaux
        y_totals = self.get_y() + 10
        x_totals = 130
        
        self.set_font('Arial', '', 10)
        self.set_xy(x_totals, y_totals)
        self.cell(40, 6, 'Sous total :', 0, 0, 'L')
        self.cell(0, 6, f"{subtotal:.0f} EU", 0, 1, 'R')
        
        self.set_xy(x_totals, y_totals + 6)
        self.cell(40, 6, f"TVA ({document_data['tva']}%) :", 0, 0, 'L')
        self.cell(0, 6, f"{tva_amount:.0f} EU", 0, 1, 'R')
        
        # TOTAL avec fond noir
        self.set_fill_color(0, 0, 0)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 12)
        self.set_xy(x_totals, y_totals + 15)
        self.cell(40, 10, 'TOTAL :', 1, 0, 'L', True)
        self.cell(0, 10, f"{total:.0f} EU", 1, 1, 'R', True)
        
        # Ligne de séparation
        self.set_text_color(0, 0, 0)
        y_footer = self.get_y() + 10
        self.set_line_width(0.5)
        self.line(margin, y_footer, page_width - margin, y_footer)
        
        # Informations de paiement
        y_payment = y_footer + 8
        self.set_font('Arial', 'B', 9)
        self.set_xy(margin, y_payment)
        self.cell(0, 5, f"Paiement a l'ordre de {document_data['my_name']}", 0, 1)
        
        self.set_font('Arial', '', 8)
        self.set_text_color(128, 128, 128)
        self.set_xy(margin, y_payment + 5)
        if 'bank_account' in document_data:
            self.cell(0, 4, f"N  de compte {document_data['bank_account']}", 0, 1)
        
        # Conditions de paiement (droite)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(0, 0, 0)
        self.set_xy(120, y_payment)
        self.cell(0, 5, 'Conditions de paiement', 0, 1, 'R')
        
        self.set_font('Arial', '', 8)
        self.set_text_color(128, 128, 128)
        self.set_xy(120, y_payment + 5)
        payment_terms = document_data.get('payment_terms', '30 jours')
        self.cell(0, 4, f"Paiement sous {payment_terms}", 0, 1, 'R')
        
        # Message de remerciement
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', 'B', 9)
        self.set_xy(margin, y_payment + 15)
        
        if doc_type.upper() == 'DEVIS':
            self.cell(0, 5, 'MERCI POUR VOTRE CONFIANCE', 0, 1, 'C')
        else:
            self.cell(0, 5, 'MERCI DE VOTRE CONFIANCE', 0, 1, 'C')


def generate_invoice_pdf(doc_type, my_info, client_info, items, total=None):
    """
    Crée un fichier PDF avec les infos données.
    
    Args:
        doc_type: 'Devis' ou 'Facture'
        my_info: Dictionnaire {name, siret (optionnel), phone, email, website (optionnel), address}
        client_info: Dictionnaire {name, phone, address}
        items: Liste de prestations [{'description': '...', 'price': ..., 'quantity': ...}]
        total: (ignoré, calculé automatiquement)
    
    Returns:
        filename: nom du fichier généré
    """
    
    # Préparer les données pour le générateur
    document_data = {
        'number': datetime.now().strftime('%Y%m%d%H%M'),
        'date': datetime.now().strftime('%d/%m/%y'),
        'my_name': my_info.get('name', 'VOTRE NOM'),
        'my_siret': my_info.get('siret', ''),
        'my_phone': my_info.get('phone', ''),
        'my_email': my_info.get('email', ''),
        'my_website': my_info.get('website', ''),
        'my_address': my_info.get('address', ''),
        'client_name': client_info.get('name', ''),
        'client_phone': client_info.get('phone', ''),
        'client_address': client_info.get('address', ''),
        'items': items,
        'tva': my_info.get('tva', 20),
        'payment_terms': my_info.get('payment_terms', '30 jours'),
        'bank_account': my_info.get('bank_account', '')
    }
    
    # Générer le PDF
    pdf = DocumentGenerator()
    pdf.create_document(doc_type, document_data)
    
    # Sauvegarder avec un nom unique
    filename = f"{doc_type}_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
    pdf.output(filename)
    
    print(f"✓ {doc_type} generé : {filename}")
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