import re
from datetime import datetime

_DIAS = {
    "lunes":"Lun","martes":"Mar","miercoles":"Mie","miércoles":"Mie",
    "jueves":"Jue","viernes":"Vie","sabado":"Sab","sábado":"Sab","domingo":"Dom"
}

def normaliza_descuento(texto:str):
    if not texto: return {"tipo":"desconocido","valor":None,"texto":""}
    t = texto.strip()
    m = re.search(r'(\d{1,3})\s*%|\-(\d{1,3})\s*%', t)
    if m:
        v = int(m.group(1) or m.group(2))
        return {"tipo":"porcentaje","valor":v,"texto":t}
    m = re.search(r'\$?\s?(\d{1,3}(?:\.\d{3})+|\d+)\s*(?:CLP|pesos|\$)', t, re.I)
    if m:
        v = int(re.sub(r'\.','',m.group(1)))
        return {"tipo":"monto","valor":v,"texto":t}
    return {"tipo":"texto","valor":None,"texto":t}

def normaliza_dias(texto:str):
    if not texto: return []
    t = texto.lower()
    res = []
    for k,v in _DIAS.items():
        if k in t: res.append(v)
    if "lunes a viernes" in t and not res: res = ["Lun","Mar","Mie","Jue","Vie"]
    if "fin de semana" in t or ("sab" in t and "dom" in t): 
        for d in ["Sab","Dom"]:
            if d not in res: res.append(d)
    return sorted(set(res), key=["Lun","Mar","Mie","Jue","Vie","Sab","Dom"].index)

def normaliza_vigencia(texto:str):
    if not texto: return {"desde":None,"hasta":None,"texto":""}
    t = texto
    # dd/mm/yyyy ó dd/mm
    m = re.search(r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?', t)
    if m:
        d,mn,y = m.group(1), m.group(2), m.group(3) or str(datetime.utcnow().year)
        if len(y)==2: y = "20"+y
        try:
            iso = datetime(int(y), int(mn), int(d)).date().isoformat()
            return {"desde":None,"hasta":iso,"texto":t}
        except: pass
    if "hasta" in t.lower(): return {"desde":None,"hasta":None,"texto":t}
    return {"desde":None,"hasta":None,"texto":t}

def normaliza_horario(texto:str):
    if not texto: return None
    t = texto.replace("hrs","").replace("horas","")
    m = re.findall(r'(\d{1,2})[:\.]?(\d{0,2})', t)
    if len(m)>=2:
        a = f"{m[0][0]}:{m[0][1] or '00'}"
        b = f"{m[1][0]}:{m[1][1] or '00'}"
        return f"{a}–{b}"
    return None
