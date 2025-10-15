from pathlib import Path
import re

URL_RE = re.compile(r'https?://[^\s)\]">]+')

def parse_ficha(fpath: Path):
    txt = fpath.read_text(encoding="utf-8")
    def pick(key, default=""):
        m = re.search(rf'^{key}:\s*(.+)$', txt, flags=re.M)
        return (m.group(1).strip() if m else default).strip()

    emisor = pick("emisor") or fpath.parent.name
    categoria = pick("categorías")
    portal = pick("portal_principal")
    requiere_js = pick("requiere_js","falso").lower().startswith("verdad")

    selectores = {}
    sbloc = re.search(r"selectores_clave:\s*(.+?)(?:\n\S|$)", txt, flags=re.S|re.M)
    if sbloc:
        for m in re.finditer(r'-\s*campo:\s*([^\n]+)\n\s*selector:\s*"([^"]+)"', sbloc.group(1)):
            selectores[m.group(1).strip()] = m.group(2).strip()

    rutas = []
    rbloc = re.search(r"rutas_base:\s*(.+?)(?:\n\S|$)", txt, flags=re.S|re.M)
    if rbloc:
        for line in rbloc.group(1).splitlines():
            if line.strip().startswith("- "):
                u = line.strip()[2:].strip()
                mu = URL_RE.search(u)
                if mu: rutas.append(mu.group(0))

    return {
        "emisor": emisor,
        "categoria": categoria,
        "portal_principal": portal,
        "requiere_js": requiere_js,
        "selectores": selectores,
        "rutas_base": rutas
    }

def collect_urls(emisor_dir: Path, portal: str, rutas_base: list, urls_filename="urls.txt"):
    urls = set()
    uf = emisor_dir / urls_filename
    if uf.exists():
        for line in uf.read_text(encoding="utf-8").splitlines():
            mu = URL_RE.search(line)
            if mu: urls.add(mu.group(0).strip())
    if portal:
        urls.add(portal)
    for u in rutas_base:
        urls.add(u)
    return [u for u in urls if u.startswith("http")]
