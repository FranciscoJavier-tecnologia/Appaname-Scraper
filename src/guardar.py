import json
from pathlib import Path
from datetime import datetime, timezone

BASE_OUT = Path("data")
CONSOLIDADO = BASE_OUT / "consolidado"

def ruta_emisor(categoria_slug:str, emisor_slug:str):
    return BASE_OUT / categoria_slug / emisor_slug

def save_snapshot(categoria_slug, emisor_slug, payload:dict):
    d = ruta_emisor(categoria_slug, emisor_slug)
    d.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).date().isoformat()
    (d / f"{ts}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (d / "latest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def save_consolidado(nombre:str, data:dict):
    CONSOLIDADO.mkdir(parents=True, exist_ok=True)
    (CONSOLIDADO / f"{nombre}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
