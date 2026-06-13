"""
sync_files.py — Carica foto e XML su NocoDB (universale)
Legge la configurazione da config.py — non modificare questo file.
"""

import os
import requests
from config import (
    NOCODB_URL, API_TOKEN, TABLE_ID, ID_COLUMN,
    ARCHIVIO_ROOT, CARTELLA_SIP, CARTELLA_AIP,
    CARTELLA_FOTO, CARTELLA_META,
    FOTO_FIELDS, XML_FIELDS
)

HEADERS_JSON = {"xc-token": API_TOKEN, "Content-Type": "application/json"}
HEADERS_AUTH = {"xc-token": API_TOKEN}
IMG_EXTS     = [".jpg", ".jpeg", ".png", ".webp", ".tiff"]


def find_file(folder, suffix):
    if not os.path.isdir(folder):
        return None
    for f in sorted(os.listdir(folder)):
        name, ext = os.path.splitext(f)
        if name.lower().endswith(suffix.lower()) and ext.lower() in IMG_EXTS + [".xml"]:
            return os.path.join(folder, f)
    return None


def fetch_all_records():
    records = {}
    offset, limit = 0, 200
    # Costruisce la lista campi da scaricare
    all_fields = list(FOTO_FIELDS.keys()) + list(XML_FIELDS.keys())
    fields_str = ",".join(["Id", ID_COLUMN] + all_fields)
    while True:
        r = requests.get(
            f"{NOCODB_URL}/api/v2/tables/{TABLE_ID}/records",
            headers=HEADERS_JSON,
            params={"limit": limit, "offset": offset, "fields": fields_str}
        )
        if not r.ok:
            print(f"❌ Errore fetch: {r.text[:120]}")
            break
        data = r.json()
        for rec in data.get("list", []):
            key = str(rec.get(ID_COLUMN, "")).strip()
            if key:
                records[key] = rec
        total = data.get("pageInfo", {}).get("totalRows", 0)
        offset += limit
        if offset >= total or len(data.get("list", [])) < limit:
            break
    return records


def upload_image(filepath):
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".webp": "image/webp", ".tiff": "image/tiff"}
    mime = mime_map.get(ext, "image/jpeg")
    with open(filepath, "rb") as f:
        r = requests.post(
            f"{NOCODB_URL}/api/v2/storage/upload",
            headers=HEADERS_AUTH,
            files={"file": (filename, f, mime)},
            params={"path": f"nocodb/uploads/{filename}"}
        )
    if not r.ok:
        print(f"    ❌ Upload fallito: {r.text[:120]}")
        return None
    result = r.json()
    return result if isinstance(result, list) else [result]


def read_xml(filepath):
    for enc in ["utf-8", "latin-1", "utf-8-sig"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return None


def is_populated(rec, field):
    val = rec.get(field)
    if not val:
        return False
    if isinstance(val, list):
        return len(val) > 0
    if isinstance(val, str):
        return val.strip() not in ("", "[]", "null")
    return True


def patch_record(row_id, updates):
    r = requests.patch(
        f"{NOCODB_URL}/api/v2/tables/{TABLE_ID}/records",
        headers=HEADERS_JSON,
        json={"Id": row_id, **updates}
    )
    return r.ok, r.text


def sync():
    print(f"\n📁 File Sync")
    print(f"   Archivio : {os.path.abspath(ARCHIVIO_ROOT)}\n")

    if not os.path.isdir(ARCHIVIO_ROOT):
        print(f"❌ Cartella non trovata: {os.path.abspath(ARCHIVIO_ROOT)}")
        return

    sip_root = os.path.join(ARCHIVIO_ROOT, CARTELLA_SIP)
    aip_root = os.path.join(ARCHIVIO_ROOT, CARTELLA_AIP)

    identificatori = sorted([
        d for d in os.listdir(sip_root)
        if os.path.isdir(os.path.join(sip_root, d))
    ]) if os.path.isdir(sip_root) else []

    print(f"📂 {len(identificatori)} oggetti nel SIP")
    print("📥 Scarico record da NocoDB...")
    all_records = fetch_all_records()
    print(f"   {len(all_records)} record trovati\n")

    tot_upload = tot_skip = tot_err = tot_miss = 0

    for idf in identificatori:
        print(f"  📦 {idf}")

        if idf not in all_records:
            print(f"     ⚠️  Non in NocoDB — skip")
            tot_miss += 1
            continue

        rec    = all_records[idf]
        row_id = rec.get("Id")
        updates = {}

        # ── FOTO (da SIP) ─────────────────────────────
        foto_dir = os.path.join(sip_root, idf, CARTELLA_FOTO)
        for field, suffix in FOTO_FIELDS.items():
            if is_populated(rec, field):
                print(f"     ✓  {field} già presente")
                tot_skip += 1
                continue
            filepath = find_file(foto_dir, suffix)
            if not filepath:
                print(f"     –  {field} ({suffix}) non trovato")
                continue
            print(f"     ⬆️  Upload {os.path.basename(filepath)} → {field}")
            result = upload_image(filepath)
            if result:
                updates[field] = result
                tot_upload += 1
            else:
                tot_err += 1

        # ── XML (da AIP) ──────────────────────────────
        meta_dir = os.path.join(aip_root, idf, CARTELLA_META)
        for field, suffix in XML_FIELDS.items():
            if is_populated(rec, field):
                print(f"     ✓  {field} già presente")
                tot_skip += 1
                continue
            filepath = find_file(meta_dir, suffix)
            if not filepath:
                print(f"     –  {field} ({suffix}) non trovato")
                continue
            print(f"     📄 Leggo {os.path.basename(filepath)} → {field}")
            content = read_xml(filepath)
            if content:
                updates[field] = content
                tot_upload += 1
            else:
                print(f"     ❌ Impossibile leggere {filepath}")
                tot_err += 1

        # ── PATCH ─────────────────────────────────────
        if updates:
            ok, err = patch_record(row_id, updates)
            if ok:
                print(f"     ✅ Record aggiornato ({len(updates)} campi)")
            else:
                print(f"     ❌ Patch fallita: {err[:100]}")
                tot_err += 1
        else:
            print(f"     — Nessun aggiornamento")

    print(f"\n{'='*50}")
    print(f"✅ FILE SYNC COMPLETATO")
    print(f"   Caricati  : {tot_upload}")
    print(f"   Già pres. : {tot_skip}")
    print(f"   Non in DB : {tot_miss}")
    print(f"   Errori    : {tot_err}")


if __name__ == "__main__":
    sync()
