"""Gera thaumora.html a partir de data/mods.json + dados do Modrinth.

Uso:  python tools/build_page.py            (usa cache se existir)
      python tools/build_page.py --refresh  (consulta o Modrinth de novo)
"""
import datetime
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "mods.json"
CACHE = ROOT / "data" / "modrinth_cache.json"
TEMPLATE = ROOT / "tools" / "page.template.html"
OUT = ROOT / "thaumora.html"
UA = {"User-Agent": "thaumora-modpack-page/1.0"}

GROUPS = [
    ["1.21.1"],
    ["1.21.2", "1.21.3", "1.21.4", "1.21.5", "1.21.6", "1.21.7", "1.21.8"],
    ["1.21.9", "1.21.10", "1.21.11"],
    ["26.1", "26.1.1", "26.1.2"],
    ["26.2"],
    ["26.3"],
]


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch(slugs):
    out = {}
    for i in range(0, len(slugs), 50):
        chunk = slugs[i:i + 50]
        ids = urllib.parse.quote(json.dumps(chunk))
        for p in get(f"https://api.modrinth.com/v2/projects?ids={ids}"):
            gallery = sorted(p.get("gallery") or [], key=lambda g: (not g.get("featured"), g.get("ordering", 0)))
            out[p["slug"]] = {
                "id": p["id"],
                "icon": p.get("icon_url"),
                "img": gallery[0]["url"] if gallery else None,
                "dl": p.get("downloads", 0),
            }
    for slug in slugs:
        if slug not in out:
            continue
        neo, other = set(), set()
        for v in get(f"https://api.modrinth.com/v2/project/{slug}/version"):
            (neo if "neoforge" in v["loaders"] else other).update(v["game_versions"])
        code = ""
        for g in GROUPS:
            code += "n" if neo & set(g) else ("o" if other & set(g) else "x")
        out[slug]["ver"] = code
        time.sleep(0.1)
    return out


def main():
    mods = json.loads(DATA.read_text(encoding="utf-8"))
    slugs = [m["mr"] for m in mods if m.get("mr")]
    if CACHE.exists() and "--refresh" not in sys.argv:
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    else:
        cache = {}
    missing = [s for s in slugs if s not in cache]
    if missing:
        cache.update(fetch(missing))
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

    # descrições detalhadas (data/info/*.json, chave = nome do mod)
    details = {}
    for f in sorted((DATA.parent / "info").glob("*.json")):
        details.update(json.loads(f.read_text(encoding="utf-8")))

    problems = []
    for m in mods:
        if m["n"] in details:
            m["info"] = {k: v for k, v in details[m["n"]].items() if k != "fonte"}
        info = cache.get(m.get("mr") or "")
        if m.get("mr") and not info:
            problems.append(f"slug nao encontrado no Modrinth: {m['mr']}")
            continue
        if info:
            m["icon"], m["img"], m["dl"] = info["icon"], info["img"], info["dl"]
            m["ver"] = m.get("ver") or info["ver"]
            if m["s"] != "no" and info["ver"][0] != "n":
                problems.append(f"sem NeoForge 1.21.1: {m['n']} ({m['mr']})")
        m["url"] = (f"https://modrinth.com/mod/{m['mr']}" if m.get("mr")
                    else f"https://www.curseforge.com/minecraft/mc-mods/{m['cf']}")

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__MODS_JSON__", json.dumps(mods, ensure_ascii=False))
    html = html.replace("__BUILD_DATE__", datetime.date.today().strftime("%d/%m/%Y"))
    OUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"ok: {len(mods)} mods -> {OUT.name}")
    for p in problems:
        print("AVISO:", p)


if __name__ == "__main__":
    main()
