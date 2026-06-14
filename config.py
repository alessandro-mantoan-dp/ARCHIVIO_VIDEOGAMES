"""
config.py — ⭐ L'UNICO FILE CHE MODIFICHI PER OGNI PROGETTO

Istruzioni:
1. Copia questo file nel tuo progetto
2. Compila la sezione "CONFIGURAZIONE PROGETTO"
3. Non toccare nient'altro

"""

# ==============================================================================
# CONFIGURAZIONE PROGETTO
# Modifica questa sezione per ogni nuovo archivio
# ==============================================================================

# ── Identità del progetto ──────────────────────────────
PROJECT_NAME  = "Archivio Videogames"          # Nome mostrato nell'interfaccia
PROJECT_EMOJI = "🎮"                    # Emoji nell'header (facoltativo)
PROJECT_SUB   = "Database Videogames"        # Sottotitolo nell'header

# ── NocoDB ────────────────────────────────────────────
NOCODB_URL  = "https://app.nocodb.com"
API_TOKEN   = "nc_pat_0xOMrFGue6orRAPn6OTgcDo306xl49DzkILRXI7d"                    # Il tuo token (per script locali)
TABLE_ID    = "miua2x3vnpojoui"         # ID tabella principale
BASE_ID     = "pves0p87dzvhrdc"         # ID base/progetto

# ── Colonna identificatore univoco ────────────────────
# Deve esistere sia in Excel che in NocoDB
ID_COLUMN   = "IDENTIFICATORE"

# ── Colonne da mostrare in evidenza nella scheda dettaglio ──
# Queste appaiono in cima alla scheda quando clicchi una riga
# Lascia vuoto [] per mostrarle tutte
HIGHLIGHT_FIELDS = []

# ── Campi foto ────────────────────────────────────────
# Formato: { "NOME_CAMPO_NOCODB": "suffisso_nel_nome_file" }
# Il suffisso viene cercato nel nome file dentro la cartella foto/
# Es. "DIP-001_fronte.jpg" ha suffisso "_fronte"
FOTO_FIELDS = {
    "FOTO_FRONTE": "_case_fronte",
    "FOTO_RETRO":  "_case_retro",
    "FOTO_SUPPORTO_FRONTE":  "_supp_fronte",
    "FOTO_SUPPORTO_RETRO":  "_supp_retro",
    # Aggiungi altre foto qui, es:
    # "FOTO_DETTAGLIO": "_supp_fronte",
    # "FOTO_FIRMA":     "_firma",
}

# ── Campi XML ─────────────────────────────────────────
# Formato: { "NOME_CAMPO_NOCODB": "suffisso_nel_nome_file" }
# Es. "DIP-001_MODS.xml" ha suffisso "_MODS"
XML_FIELDS = {
    "XML_MODS":   "_MODS",
    "XML_PREMIS": "_PREMIS",
    # Aggiungi altri XML qui, es:
    # "XML_DC": "_DC",
}

# ── Cartelle archivio (per sync_files.py) ────────────
ARCHIVIO_ROOT = "."
CARTELLA_SIP  = "01_SIP"
CARTELLA_AIP  = "02_AIP"
CARTELLA_FOTO = "foto"          # nome sottocartella foto dentro SIP
CARTELLA_META = "metadata"      # nome sottocartella XML dentro AIP

# ── File Excel (per sync_excel.py) ───────────────────
EXCEL_FILE = "ARCHIVIO_VIDEOGAMES.xlsx"
EXCEL_SHEETS = [
    {
        "sheet":      "VIDEOGAMES",
        "table_id":   TABLE_ID,
        "header_row": 1,
        "parent":     None,
        "parent_fk":  None,
        "field_transforms": {
            "COLORE":             lambda v: fix_colore(v),
            "DATA ACQUISIZIONE":  lambda v: fix_date(v),
            "DATA PUBBLICAZIONE": lambda v: fix_date(v),
        },
        "skip_columns": [],
    },
    # Aggiungi altri fogli se hai tabelle collegate, es:
    # {
    #     "sheet":     "TESTI CARTE",
    #     "table_id":  "xxxx_id_tabella_testi",
    #     "header_row": 1,
    #     "parent":    "CARTE",
    #     "parent_fk": "carta_id",
    #     "field_transforms": {},
    #     "skip_columns": [],
    # },
]

# ── Campi da nascondere nella tabella principale ───────
# (vengono mostrati solo nella scheda dettaglio)
# Di default nasconde automaticamente i campi foto e XML
# Aggiungi qui altri campi da nascondere dalla tabella
HIDE_FROM_TABLE = [
      "FOTO_FRONTE",
      "FOTO_RETRO",
      "FOTO_SUPPORTO_FRONTE",
      "FOTO_SUPPORTO_RETRO",
      "XML_MODS",
      "XML_PREMIS",
]

# ==============================================================================
# FUNZIONI DI TRASFORMAZIONE
# Aggiungi qui le funzioni per pulire/normalizzare i dati dell'Excel
# ==============================================================================

import pandas as pd

def fix_date(val, fmt="%Y-%m-%d"):
    """Converte qualsiasi formato data in YYYY-MM-DD"""
    if val is None or str(val).strip() == "":
        return None
    try:
        return pd.to_datetime(val).strftime(fmt)
    except:
        return None

def fix_number(val):
    """Converte stringhe numeriche in float (gestisce virgole e simboli €)"""
    if val is None or str(val).strip() == "":
        return None
    try:
        return float(str(val).replace(",", ".").replace("€", "").replace("$", "").strip())
    except:
        return None

def fix_enum(val, mapping: dict):
    """
    Normalizza valori secondo una mappa.
    Es: fix_enum(val, {"R": "Rosso", "B": "Blu", "W": "Bianco"})
    """
    if val is None or str(val).strip() == "":
        return None
    return mapping.get(str(val).strip().upper(), str(val).strip())

def fix_bool(val):
    """Converte vari formati booleani in True/False"""
    if val is None or str(val).strip() == "":
        return None
    return str(val).strip().upper() in ("1", "SI", "SÌ", "YES", "TRUE", "X", "V")

def fix_colore(val):
    """Specifico per carte MTG — normalizza i codici colore"""
    if val is None or str(val).strip() == "":
        return None
    mapping = {
        "C": "C", "R/W": "R/W", "W/R": "R/W",
        "U/B": "U/B", "B/U": "U/B", "B/R": "B/R",
        "R/B": "B/R", "R/U": "U/R", "U/R": "U/R"
    }
    return mapping.get(str(val).strip().upper(), str(val).strip())


# ==============================================================================
# ESEMPI PER ALTRI TIPI DI OGGETTO
# Copia e adatta la sezione CONFIGURAZIONE PROGETTO qui sopra
# ==============================================================================

"""
──────────────────────────────────────────────
ESEMPIO: ARCHIVIO DIPINTI
──────────────────────────────────────────────
PROJECT_NAME  = "Archivio Dipinti"
PROJECT_EMOJI = "🖼️"
PROJECT_SUB   = "Collezione d'Arte"

TABLE_ID    = "xxxx_dipinti"
BASE_ID     = "xxxx_base"
ID_COLUMN   = "IDENTIFICATORE"

HIGHLIGHT_FIELDS = ["IDENTIFICATORE", "TITOLO", "AUTORE", "ANNO", "TECNICA"]

FOTO_FIELDS = {
    "FOTO_FRONTE":    "_fronte",
    "FOTO_DETTAGLIO": "_dettaglio",
    "FOTO_RETRO":     "_retro",
    "FOTO_FIRMA":     "_firma",
}

XML_FIELDS = {
    "XML_MODS":   "_MODS",
    "XML_PREMIS": "_PREMIS",
}

ARCHIVIO_ROOT = "./archivio_dipinti"

EXCEL_SHEETS = [
    {
        "sheet":      "DIPINTI",
        "table_id":   TABLE_ID,
        "header_row": 0,
        "parent":     None,
        "parent_fk":  None,
        "field_transforms": {
            "ANNO":            lambda v: fix_number(v),
            "DATA ACQUISTO":   lambda v: fix_date(v),
            "PREZZO":          lambda v: fix_number(v),
        },
        "skip_columns": ["NOTE PRIVATE"],
    },
]

──────────────────────────────────────────────
ESEMPIO: ARCHIVIO OROLOGI
──────────────────────────────────────────────
PROJECT_NAME  = "Archivio Orologi"
PROJECT_EMOJI = "⌚"
PROJECT_SUB   = "Collezione Segnatempo"

TABLE_ID    = "xxxx_orologi"
BASE_ID     = "xxxx_base"
ID_COLUMN   = "IDENTIFICATORE"

HIGHLIGHT_FIELDS = ["IDENTIFICATORE", "MARCA", "MODELLO", "ANNO", "MOVIMENTO", "CONDIZIONE"]

FOTO_FIELDS = {
    "FOTO_QUADRANTE": "_quadrante",
    "FOTO_FONDELLO":  "_fondello",
    "FOTO_LATERALE":  "_laterale",
    "FOTO_BRACCIALE": "_bracciale",
}

XML_FIELDS = {
    "XML_MODS":   "_MODS",
    "XML_PREMIS": "_PREMIS",
}

ARCHIVIO_ROOT = "./archivio_orologi"

EXCEL_SHEETS = [
    {
        "sheet":      "OROLOGI",
        "table_id":   TABLE_ID,
        "header_row": 0,
        "parent":     None,
        "parent_fk":  None,
        "field_transforms": {
            "ANNO":           lambda v: fix_number(v),
            "PREZZO ACQUISTO": lambda v: fix_number(v),
            "DATA ACQUISTO":  lambda v: fix_date(v),
            "FUNZIONANTE":    lambda v: fix_bool(v),
        },
        "skip_columns": [],
    },
]

──────────────────────────────────────────────
ESEMPIO: ARCHIVIO VIDEOGIOCHI
──────────────────────────────────────────────
PROJECT_NAME  = "Archivio Videogiochi"
PROJECT_EMOJI = "🎮"
PROJECT_SUB   = "Collezione Gaming"

TABLE_ID    = "xxxx_videogiochi"
BASE_ID     = "xxxx_base"
ID_COLUMN   = "IDENTIFICATORE"

HIGHLIGHT_FIELDS = ["IDENTIFICATORE", "TITOLO", "PIATTAFORMA", "ANNO", "EDITORE", "CONDIZIONE"]

FOTO_FIELDS = {
    "FOTO_COPERTINA":  "_copertina",
    "FOTO_RETRO":      "_retro",
    "FOTO_CARTUCCIA":  "_cartuccia",
    "FOTO_MANUALE":    "_manuale",
}

XML_FIELDS = {
    "XML_MODS":   "_MODS",
    "XML_PREMIS": "_PREMIS",
}

ARCHIVIO_ROOT = "./archivio_videogiochi"

EXCEL_SHEETS = [
    {
        "sheet":      "VIDEOGIOCHI",
        "table_id":   TABLE_ID,
        "header_row": 0,
        "parent":     None,
        "parent_fk":  None,
        "field_transforms": {
            "ANNO":        lambda v: fix_number(v),
            "COMPLETO":    lambda v: fix_bool(v),
            "FUNZIONANTE": lambda v: fix_bool(v),
        },
        "skip_columns": [],
    },
]
"""
