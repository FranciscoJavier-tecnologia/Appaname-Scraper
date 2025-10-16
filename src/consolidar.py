import json
from pathlib import Path

BASE = Path("data")
OUT = BASE / "consolidado"
OUT.mkdir(parents=True, exist_ok=True)

def collect(cat):
    d = BASE / cat
    data = {}
    if not d.exists(): return data
    for emdir in d.iterdir():
        f = emdir / "latest.json"
        if f.exists():
            try:
                data[emdir.name] = json.loads(f.read_text(encoding="utf-8"))
            except: pass
    return data

def main():
    cats = ["bancos-tarjetas","minorista-comercio","isapres-salud","caja-compensacion"]
    for c in cats:
        data = collect(c)
        (OUT / f"{c.split('-')[0]}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("✅ Consolidado generado en data/consolidado/")
if __name__ == "__main__":
    main()
