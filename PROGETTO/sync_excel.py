"""
sync_excel.py — Importa Excel → NocoDB (universale)
Legge la configurazione da config.py — non modificare questo file.
"""

import requests
import pandas as pd
from config import (
    NOCODB_URL, API_TOKEN, ID_COLUMN, EXCEL_FILE, EXCEL_SHEETS
)

HEADERS = {"xc-token": API_TOKEN, "Content-Type": "application/json"}


def fetch_existing_ids(table_id):
    existing = {}
    offset, limit = 0, 200
    while True:
        r = requests.get(
            f"{NOCODB_URL}/api/v2/tables/{table_id}/records",
            headers=HEADERS,
            params={"limit": limit, "offset": offset, "fields": f"Id,{ID_COLUMN}"}
        )
        if not r.ok:
            print(f"  ⚠️  Errore fetch {table_id}: {r.text[:100]}")
            break
        data = r.json()
        for rec in data.get("list", []):
            key = str(rec.get(ID_COLUMN, "")).strip()
            if key:
                existing[key] = rec.get("Id")
        total = data.get("pageInfo", {}).get("totalRows", 0)
        offset += limit
        if offset >= total or len(data.get("list", [])) < limit:
            break
    return existing


def clean_record(row, transforms, skip_cols):
    data = row.fillna("").to_dict()
    for col in skip_cols:
        data.pop(col, None)
    for col, fn in transforms.items():
        if col in data:
            data[col] = fn(data[col])
    for k, v in data.items():
        if hasattr(v, "isoformat"):
            data[k] = v.isoformat()
    data = {k: (None if v == "" else v) for k, v in data.items()}
    return data


def post_record(table_id, data):
    r = requests.post(
        f"{NOCODB_URL}/api/v2/tables/{table_id}/records",
        headers=HEADERS, json=data
    )
    if not r.ok:
        return None, r.text
    res = r.json()
    nid = res.get("Id") or res.get("id") or (res.get("data") or {}).get("Id")
    return nid, None


def sync():
    print(f"\n📊 Excel Sync — {EXCEL_FILE}\n")
    id_maps = {}

    for cfg in EXCEL_SHEETS:
        sheet      = cfg["sheet"]
        table_id   = cfg["table_id"]
        header_row = cfg.get("header_row", 0)
        parent     = cfg.get("parent")
        parent_fk  = cfg.get("parent_fk")
        transforms = cfg.get("field_transforms", {})
        skip_cols  = cfg.get("skip_columns", [])

        print(f"{'='*50}\n📋 Foglio: {sheet}")

        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, header=header_row)
            df.columns = df.columns.str.strip()
        except Exception as e:
            print(f"  ❌ Impossibile leggere '{sheet}': {e}")
            continue

        if ID_COLUMN not in df.columns:
            print(f"  ❌ Colonna '{ID_COLUMN}' non trovata.")
            print(f"     Colonne disponibili: {list(df.columns)}")
            continue

        existing = fetch_existing_ids(table_id)
        print(f"  Già in NocoDB : {len(existing)}")
        print(f"  Righe Excel   : {len(df)}")

        id_maps[sheet] = dict(existing)
        inseriti = skippati = errori = 0

        for _, row in df.iterrows():
            idf = str(row.get(ID_COLUMN, "")).strip()
            if not idf or idf == "nan":
                continue
            if idf in existing:
                skippati += 1
                continue

            data = clean_record(row, transforms, skip_cols)

            if parent and parent_fk:
                parent_id = id_maps.get(parent, {}).get(idf)
                if parent_id is None:
                    print(f"  ⚠️  SKIP {idf} — padre non trovato")
                    continue
                data[parent_fk] = parent_id

            nid, err = post_record(table_id, data)
            if err:
                print(f"  ❌ {idf}: {err[:80]}")
                errori += 1
            else:
                id_maps[sheet][idf] = nid
                inseriti += 1
                print(f"  ✅ {idf}")

        print(f"\n  → Inseriti: {inseriti} | Skippati: {skippati} | Errori: {errori}")

    print(f"\n{'='*50}\n✅ EXCEL SYNC COMPLETATO")


if __name__ == "__main__":
    sync()
