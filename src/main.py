import json, re, os, yaml
from pathlib import Path
from datetime import datetime, timezone
import json
from pathlib import Path
from datetime import datetime
from parser_ficha import parse_ficha, collect_urls
from crawl_html import fetch_html, extract_from_html
from crawl_js import extract_with_js

# RUTA al Repositorio A (ajusta a tu ruta real si es necesario)
REPO_A = Path("../Appaname-DB")

OUT_DIR = Path("data"); OUT_DIR.mkdir(exist_ok=True, parents=True)

def iter_fichas(repo_root: Path):
    for f in repo_root.rglob("ficha.md"):
        yield f

def run():
    consolidated = {}
    for ficha_path in iter_fichas(REPO_A):
        meta = parse_ficha(ficha_path)
        emisor = meta["emisor"] or ficha_path.parent.name
        em_dir = ficha_path.parent

        urls = collect_urls(em_dir, meta["portal_principal"], meta["rutas_base"])
        result = {
            "emisor": emisor,
            "categoria": meta["categoria"],
            "requiere_js": meta["requiere_js"],
            "urls_origen": urls,
            "items": [],
            "ts": datetime.now(timezone.utc).isoformat()
        }

        for u in urls:
            try:
                if meta["requiere_js"]:
                    items = extract_with_js(u, meta["selectores"])
                else:
                    html = fetch_html(u)
                    items = extract_from_html(html, meta["selectores"])
                for it in items:
                    it["url_de_origen"] = u
                result["items"].extend(items)
            except Exception as e:
                result.setdefault("errores", []).append({"url": u, "error": str(e)})

        (OUT_DIR / f"{emisor}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        consolidated[emisor] = result

    (OUT_DIR / "all_emisores.json").write_text(json.dumps(consolidated, ensure_ascii=False, indent=2), encoding="utf-8")
    print("✅ Listo. Estructura creada. Cuando decidas, ejecuta:  python src/main.py")

if __name__ == "__main__":
    run()

# === Helpers de categoría/emisor/slug ===
def slugify(s:str):
    return re.sub(r'[^a-z0-9_]+','_', s.lower().strip().replace(" ","_"))

def detect_categoria(emisor:str, ficha_categoria:str):
    # 1) si la ficha trae categoria, úsala
    if ficha_categoria:
        return ficha_categoria
    # 2) heurística desde config/categorias.yml
    try:
        with open("config/categorias.yml", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        for cat, kw in cfg.items():
            for k in kw:
                if k.lower() in emisor.lower():
                    return cat
    except: pass
    return "otros"

from guardar import save_snapshot, save_consolidado
from normalizador import normaliza_descuento, normaliza_dias, normaliza_vigencia, normaliza_horario

# === Al terminar cada emisor, normaliza y guarda ordenado ===
def _normaliza_items(items):
    norm = []
    for it in items:
        dcto = normaliza_descuento(it.get("descuento") or it.get("descuento_texto") or "")
        dias = normaliza_dias((it.get("terminos") or it.get("terminos_hint") or ""))
        vig  = normaliza_vigencia((it.get("terminos") or it.get("terminos_hint") or ""))
        hor  = normaliza_horario((it.get("terminos") or it.get("terminos_hint") or ""))
        norm.append({
            "comercio": it.get("comerciante") or it.get("comerciante_o_beneficio") or it.get("titulo") or "",
            "descuento": dcto,
            "dias": dias,
            "horarios": hor,
            "vigencia": vig,
            "terminos": it.get("terminos") or it.get("terminos_hint") or "",
            "url_origen": it.get("url_de_origen") or it.get("url") or ""
        })
    return norm

def _guardar_por_categoria(meta, result):
    categoria_slug = detect_categoria(meta["emisor"], meta.get("categoria") or meta.get("categoria",""))
    emisor_slug = slugify(meta["emisor"])
    payload = {
        "emisor": meta["emisor"],
        "categoria": categoria_slug,
        "capturado_en": datetime.now(timezone.utc).isoformat(),
        "fuentes": result.get("urls_origen", []),
        "beneficios": _normaliza_items(result.get("items", []))
    }
    save_snapshot(categoria_slug, emisor_slug, payload)
