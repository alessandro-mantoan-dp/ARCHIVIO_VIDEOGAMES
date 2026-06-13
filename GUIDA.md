# Kit Archivio Universale — Guida Completa

## Cos'è questo kit

Un sistema completo e riutilizzabile per creare archivi digitali su NocoDB,
consultabili via web, adattabile a qualsiasi tipologia di oggetto:
carte, dipinti, orologi, statue, videogiochi, libri, monete, ecc.

---

## Struttura del kit

```
archivio-universale/
  ├── GUIDA.md                  ← questa guida
  ├── config.py                 ← ⭐ IL FILE CHE MODIFICHI PER OGNI PROGETTO
  ├── main.py                   ← backend FastAPI (non toccare)
  ├── sync_excel.py             ← importa Excel → NocoDB (non toccare)
  ├── sync_files.py             ← carica foto e XML (non toccare)
  ├── requirements.txt          ← dipendenze (non toccare)
  ├── render.yaml               ← config deploy (non toccare)
  └── static/
        └── index.html          ← frontend (non toccare)
```

**La regola fondamentale: modifichi SOLO `config.py`.**
Tutto il resto si adatta automaticamente.

---

## Flusso di lavoro per un nuovo progetto

### Passo 1 — Crea il database su NocoDB

1. Vai su https://app.nocodb.com
2. Crea un nuovo Base (es. "Archivio Dipinti")
3. Crea la tabella principale (es. "DIPINTI") con queste colonne obbligatorie:
   - `IDENTIFICATORE` — tipo **Text** — chiave univoca (es. DIP-001-001)
   - Tutte le colonne descrittive che vuoi (es. TITOLO, AUTORE, ANNO, ecc.)
4. Se vuoi foto aggiungi colonne tipo **Attachment**:
   - Es. `FOTO_FRONTE`, `FOTO_RETRO`, `FOTO_DETTAGLIO`
5. Se vuoi XML aggiungi colonne tipo **Long Text**:
   - Es. `XML_MODS`, `XML_PREMIS`
6. Se hai una seconda tabella collegata (es. RESTAURI) aggiungila con FK

### Passo 2 — Recupera gli ID da NocoDB

Dall'URL della tabella:
```
https://app.nocodb.com/WORKSPACE/BASE_ID/TABLE_ID/VIEW_ID/nome-tabella
```
- `BASE_ID`  → es. `pnb04i444j42xp9`
- `TABLE_ID` → es. `mc04y78gy63ahtx`

### Passo 3 — Modifica config.py

Apri `config.py` e compila la sezione per il tuo progetto.
È l'unico file che tocchi. Vedi il file per i dettagli.

### Passo 4 — Prepara Excel e cartelle file

**Excel:** una riga per oggetto, prima colonna = IDENTIFICATORE
**Cartelle:**
```
archivio/
  01_SIP/
    DIP-001-001/
      foto/
        DIP-001-001_fronte.jpg
        DIP-001-001_retro.jpg
  02_AIP/
    DIP-001-001/
      metadata/
        DIP-001-001_MODS.xml
        DIP-001-001_PREMIS.xml
```

### Passo 5 — Importa i dati

```bash
# Importa Excel
python sync_excel.py

# Carica foto e XML
python sync_files.py
```

### Passo 6 — Deploy su Render

```bash
git add .
git commit -m "nuovo archivio dipinti"
git push
```
Render rideploya automaticamente.

---

## Cosa personalizzare per ogni tipo di oggetto

### Colonne descrittive
Ogni oggetto ha caratteristiche diverse. Esempi:

| Tipo oggetto | Colonne tipiche |
|---|---|
| Dipinti | TITOLO, AUTORE, ANNO, TECNICA, DIMENSIONI, PROVENIENZA |
| Orologi | MARCA, MODELLO, ANNO, MOVIMENTO, MATERIALE, NUMERO_SERIE |
| Statue | TITOLO, AUTORE, MATERIALE, ALTEZZA, PERIODO, PROVENIENZA |
| Videogiochi | TITOLO, PIATTAFORMA, ANNO, EDITORE, CONDIZIONE, REGIONE |
| Libri antichi | TITOLO, AUTORE, ANNO, EDITORE, LINGUA, EDIZIONE |
| Monete | PAESE, ANNO, DENOMINAZIONE, METALLO, ZECCA, CONDIZIONE |

### Foto
Puoi avere quante foto vuoi — aggiungile in `config.py`:
```python
FOTO_FIELDS = {
    "FOTO_FRONTE":    "_fronte",     # suffisso nel nome file
    "FOTO_RETRO":     "_retro",
    "FOTO_DETTAGLIO": "_dettaglio",  # aggiungi quante ne vuoi
    "FOTO_FIRMA":     "_firma",
}
```

### Scheda dettaglio
Nella scheda che si apre cliccando una riga puoi scegliere:
- Quali campi mostrare in evidenza (in cima alla scheda)
- Quali foto mostrare
- Se mostrare XML MODS/PREMIS
- Campi da nascondere dalla tabella principale

Tutto configurabile in `config.py`.

---

## Esempi di configurazione per tipo di oggetto

Vedi i commenti in `config.py` — ci sono esempi pronti per:
- Carte MTG (già usato)
- Dipinti
- Orologi
- Statue
- Videogiochi

---

## Troubleshooting

**Errore 404 alla connessione**
→ Controlla TABLE_ID e BASE_ID in config.py / variabili Render

**Foto non visibili**
→ Verifica che il campo in NocoDB sia tipo "Attachment"
→ Controlla il suffisso file in FOTO_FIELDS

**XML non compare**
→ Verifica che il campo in NocoDB sia tipo "Long Text"
→ Controlla XML_FIELDS in config.py

**Doppioni all'importazione Excel**
→ Verifica che ID_COLUMN in config.py corrisponda esattamente
   al nome della colonna in NocoDB e nell'Excel
