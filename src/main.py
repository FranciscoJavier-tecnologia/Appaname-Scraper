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
            "ts": datetime.utcnow().isoformat()+"Z"
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
