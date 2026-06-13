"""
main.py — Backend FastAPI universale
Legge la configurazione da variabili d'ambiente (Render) o da config.py
Non modificare questo file.
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import httpx
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Legge da env vars (Render) con fallback a config.py
try:
    from config import NOCODB_URL as _URL, TABLE_ID as _TID, BASE_ID as _BID
except ImportError:
    _URL = _TID = _BID = ""

NOCODB_URL = os.environ.get("NOCODB_URL",     _URL or "https://app.nocodb.com")
API_TOKEN  = os.environ.get("NOCODB_TOKEN",   "")
TABLE_ID   = os.environ.get("NOCODB_TABLE_ID", _TID or "")
BASE_ID    = os.environ.get("NOCODB_BASE_ID",  _BID or "")

# Legge config UI da env vars o config.py
try:
    from config import (
        PROJECT_NAME, PROJECT_EMOJI, PROJECT_SUB,
        HIGHLIGHT_FIELDS, FOTO_FIELDS, XML_FIELDS, HIDE_FROM_TABLE
    )
except ImportError:
    PROJECT_NAME = "Archivio"; PROJECT_EMOJI = "🗄️"; PROJECT_SUB = ""
    HIGHLIGHT_FIELDS = []; FOTO_FIELDS = {}; XML_FIELDS = {}; HIDE_FROM_TABLE = []

HEADERS = {"xc-token": API_TOKEN, "Content-Type": "application/json"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/config")
async def get_config():
    """Espone la configurazione UI al frontend"""
    return {
        "projectName":     PROJECT_NAME,
        "projectEmoji":    PROJECT_EMOJI,
        "projectSub":      PROJECT_SUB,
        "highlightFields": HIGHLIGHT_FIELDS,
        "fotoFields":      list(FOTO_FIELDS.keys()),
        "xmlFields":       list(XML_FIELDS.keys()),
        "hideFromTable":   HIDE_FROM_TABLE + list(FOTO_FIELDS.keys()) + list(XML_FIELDS.keys()),
    }


@app.get("/api/records")
async def get_records(
    limit:  int = Query(25),
    offset: int = Query(0),
    where:  str = Query(None),
    sort:   str = Query(None),
    fields: str = Query(None),
):
    params = {"limit": limit, "offset": offset}
    if where:  params["where"]  = where
    if sort:   params["sort"]   = sort
    if fields: params["fields"] = fields

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.get(
                f"{NOCODB_URL}/api/v3/tables/{TABLE_ID}/records",
                headers=HEADERS, params=params
            )
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        r = await client.get(
            f"{NOCODB_URL}/api/v1/db/data/noco/{BASE_ID}/{TABLE_ID}",
            headers=HEADERS, params=params
        )
        if not r.is_success:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


app.mount("/", StaticFiles(directory="static", html=True), name="static")
