"""Mapeia cada mod do pack (data/lock.json + CurseForge pendentes) para o projeto e o arquivo no CurseForge.

Usa a API pública da cfwidget (api.cfwidget.com), que não pede chave. Para cada mod:
  1. acha o projeto no CurseForge pelo slug (o do Modrinth, o do campo "cf" ou os de data/cf_slugs.json);
  2. escolhe o arquivo para 1.21.1 NeoForge: de preferência o mesmo jar do lock, senão o release mais novo.

Saída: data/cf_map.json com o status de cada mod:
  mesmo_arquivo     o mesmo jar do Modrinth existe no CurseForge
  outra_versao      existe para 1.21.1 NeoForge, mas com outro arquivo/versão
  sem_versao        o projeto existe no CurseForge, mas sem arquivo 1.21.1 NeoForge
  nao_encontrado    não achado pelo slug (adicione o slug certo em data/cf_slugs.json)

Uso: python -I tools/cf_map.py [--refresh]
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "data" / "lock.json"
SLUGS = ROOT / "data" / "cf_slugs.json"      # correções manuais: {"slug-modrinth": "slug-curseforge"}
CACHE = ROOT / "data" / "cf_cache.json"
OUT = ROOT / "data" / "cf_map.json"
UA = {"User-Agent": "thaumora-modpack-builder/1.0"}
MC, LOADER = "1.21.1", "NeoForge"


def fetch(slug):
    url = f"https://api.cfwidget.com/minecraft/mc-mods/{slug}"
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                if r.status == 202:  # a cfwidget ainda está buscando o projeto; tenta de novo
                    time.sleep(5 + attempt * 5)
                    continue
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(3 + attempt * 3)
        except Exception:
            time.sleep(3 + attempt * 3)
    return None


def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def main():
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    manual = json.loads(SLUGS.read_text(encoding="utf-8")) if SLUGS.exists() else {}
    cache = {} if "--refresh" in sys.argv or not CACHE.exists() else json.loads(CACHE.read_text(encoding="utf-8"))

    def project(slug):
        if slug not in cache:
            data = fetch(slug)
            # guarda só o necessário (a descrição é grande)
            cache[slug] = None if not data else {
                "id": data["id"], "title": data["title"], "url": data["urls"]["curseforge"],
                "files": [{k: f[k] for k in ("id", "name", "display", "type", "versions", "uploaded_at")}
                          for f in data.get("files", [])]}
            time.sleep(0.3)
        return cache[slug]

    items = [{"n": m["title"], "mr": m["slug"], "file": m["file"], "client": m["client"], "server": m["server"]}
             for m in lock["mods"]]
    items += [{"n": c["n"], "cf": c["cf"], "file": None} for c in lock.get("curseforge_pendentes", [])]

    result = []
    for it in items:
        key = it.get("mr") or it["cf"]
        cands = [manual[key]] if key in manual else []
        cands += [it.get("cf"), it.get("mr"), slugify(it["n"])]
        p, used = None, None
        for c in dict.fromkeys(x for x in cands if x):
            p = project(c)
            if p:
                used = c
                break
        row = {"n": it["n"], "mr": it.get("mr"), "cf_slug": used}
        if not p:
            row["status"] = "nao_encontrado"
        else:
            row.update(cf_id=p["id"], cf_title=p["title"], cf_url=p["url"])
            ok = [f for f in p["files"] if MC in f["versions"] and LOADER in f["versions"]]
            norm = lambda s: re.sub(r"[+ ]", "-", s or "")  # o CurseForge troca "+" e espaço por "-"
            same = next((f for f in ok if it["file"] and norm(f["name"]) == norm(it["file"])), None)
            if same:
                row.update(status="mesmo_arquivo", file_id=same["id"], file=same["name"])
            elif ok:
                rank = {"release": 0, "beta": 1, "alpha": 2}
                best = min(ok, key=lambda f: (rank.get(f["type"], 3), -int(re.sub(r"\D", "", f["uploaded_at"])[:14] or 0)))
                row.update(status="outra_versao", file_id=best["id"], file=best["name"], mr_file=it["file"])
            else:
                row["status"] = "sem_versao"
        result.append(row)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    c = Counter(r["status"] for r in result)
    print(" | ".join(f"{k}: {v}" for k, v in c.most_common()))
    for r in result:
        if r["status"] in ("nao_encontrado", "sem_versao"):
            print(f"  {r['status']:15} {r['n']} ({r.get('mr') or r.get('cf_slug')})")


if __name__ == "__main__":
    main()
