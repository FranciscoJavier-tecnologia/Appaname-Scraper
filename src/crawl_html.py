import requests
from bs4 import BeautifulSoup

DEFAULT_TITLE = "h1, h2, h3, [class*=beneficio], [class*=titulo]"
DEFAULT_DISC  = ".badge, .percent, [class*=descuento], [class*=discount]"
DEFAULT_TERMS = ".tyc, .bases, .modal, [class*=terms]"

def fetch_html(url, timeout=20):
    r = requests.get(url, timeout=timeout, headers={"User-Agent":"AppanameBot/1.0"})
    r.raise_for_status()
    return r.text

def extract_from_html(html, selectores: dict, max_items=60):
    soup = BeautifulSoup(html, "html.parser")
    sel_title = selectores.get("comerciante") or selectores.get("beneficio") or DEFAULT_TITLE
    sel_disc  = selectores.get("descuento") or DEFAULT_DISC
    sel_terms = selectores.get("términos") or selectores.get("terminos") or DEFAULT_TERMS

    titles = [t.get_text(strip=True) for t in soup.select(sel_title)][:max_items]
    discs  = [d.get_text(strip=True) for d in soup.select(sel_disc)][:max_items]
    terms  = [t.get_text(strip=True) for t in soup.select(sel_terms)][:10]

    items = []
    for i, t in enumerate(titles):
        items.append({
            "comerciante_o_beneficio": t,
            "descuento": discs[i] if i < len(discs) else "",
            "terminos_hint": "; ".join(terms[:2]) if terms else ""
        })
    return items
