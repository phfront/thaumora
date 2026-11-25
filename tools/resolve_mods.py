"""Resolve as versões exatas (Minecraft 1.21.1 / NeoForge) de todos os mods do pack no Modrinth,
incluindo dependências obrigatórias, e baixa os .jar para um cache.

Saída:
  data/lock.json                              versão travada de cada mod (nome, arquivo, sha1, lado)
  ../../shared/mod-cache/<arquivo>.jar        os jars baixados

Mods que só existem no CurseForge ("cf" em mods.json) são listados em lock.json -> "curseforge_pendentes".

Uso: python -I tools/resolve_mods.py [--no-download]
"""
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODS = ROOT / "data" / "mods.json"
LOCK = ROOT / "data" / "lock.json"
CACHE = ROOT.parent.parent / "shared" / "mod-cache"
UA = {"User-Agent": "thaumora-modpack-builder/1.0"}
MC, LOADER = "1.21.1", "neoforge"


def get(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 + attempt * 3)
        except Exception:
            time.sleep(2 + attempt * 3)
    raise RuntimeError(f"falhou: {url}")


project_cache = {}


def project(pid):
    if pid not in project_cache:
        project_cache[pid] = get(f"https://api.modrinth.com/v2/project/{pid}")
    return project_cache[pid]


def best_version(pid, pin=None):
    q = urllib.parse.urlencode({"loaders": json.dumps([LOADER]), "game_versions": json.dumps([MC])})
    vs = get(f"https://api.modrinth.com/v2/project/{pid}/version?{q}") or []
    if not vs:
        return None
    if pin:
        return next((v for v in vs if v["version_number"] == pin), None)
    for vt in ("release", "beta", "alpha"):
        for v in vs:  # a API devolve do mais novo para o mais antigo
            if v["version_type"] == vt:
                return v
    return vs[0]


def main():
    mods = json.loads(MODS.read_text(encoding="utf-8"))
    wanted, cf_pending, pins = [], [], {}
    deps_file = ROOT / "data" / "deps.json"
    deps = json.loads(deps_file.read_text(encoding="utf-8")) if deps_file.exists() else {}
    for slug in deps.get("modrinth", []):
        wanted.append((slug, "dependência não declarada (deps.json)"))
    for d in deps.get("curseforge", []):
        cf_pending.append({"n": d["n"], "cf": d["cf"], "para": d.get("para")})
    for m in mods:
        if m.get("pin") and m.get("mr"):
            pins[m["mr"]] = m["pin"]
        if m["s"] == "no":
            continue
        if m.get("mr"):
            wanted.append((m["mr"], m["n"]))
        elif m.get("cf"):
            cf_pending.append({"n": m["n"], "cf": m["cf"]})
        for e in m.get("extra", []):
            wanted.append((e, f"{m['n']} (extra)"))

    resolved, problems = {}, []
    queue = list(wanted)
    while queue:
        slug, why = queue.pop(0)
        p = project(slug)
        if not p:
            problems.append(f"projeto não encontrado: {slug} ({why})")
            continue
        pid = p["id"]
        if pid in resolved:
            continue
        v = best_version(pid, pins.get(p["slug"]))
        if not v:
            problems.append(f"sem versão {MC} {LOADER}: {p['title']} ({why})")
            continue
        f = next((x for x in v["files"] if x["primary"]), v["files"][0])
        resolved[pid] = {
            "slug": p["slug"], "title": p["title"], "version": v["version_number"], "type": v["version_type"],
            "file": f["filename"], "url": f["url"], "sha1": f["hashes"]["sha1"], "size": f["size"],
            "client": p["client_side"], "server": p["server_side"], "via": why,
        }
        for d in v["dependencies"]:
            if d["dependency_type"] == "required" and d.get("project_id"):
                queue.append((d["project_id"], f"dependência de {p['title']}"))
            if d["dependency_type"] == "incompatible" and d.get("project_id"):
                resolved[pid].setdefault("incompatible", []).append(d["project_id"])
        time.sleep(0.05)

    # conflitos declarados entre mods do próprio pack
    for pid, r in resolved.items():
        for bad in r.get("incompatible", []):
            if bad in resolved:
                problems.append(f"incompatível declarado: {r['title']} x {resolved[bad]['title']}")

    lock = {"minecraft": MC, "loader": LOADER, "mods": sorted(resolved.values(), key=lambda r: r["title"].lower()),
            "curseforge_pendentes": cf_pending, "problemas": problems}
    LOCK.write_text(json.dumps(lock, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"resolvidos: {len(resolved)} jars | CurseForge pendentes: {len(cf_pending)} | problemas: {len(problems)}")
    for pr in problems:
        print("  !", pr)

    if "--no-download" in sys.argv:
        return
    CACHE.mkdir(parents=True, exist_ok=True)
    total = 0
    for r in lock["mods"]:
        dest = CACHE / r["file"]
        if dest.exists() and hashlib.sha1(dest.read_bytes()).hexdigest() == r["sha1"]:
            continue
        with urllib.request.urlopen(urllib.request.Request(r["url"], headers=UA), timeout=120) as resp:
            data = resp.read()
        if hashlib.sha1(data).hexdigest() != r["sha1"]:
            raise RuntimeError(f"sha1 não confere: {r['file']}")
        dest.write_bytes(data)
        total += len(data)
    print(f"download ok ({total / 1e6:.0f} MB novos) -> {CACHE}")


if __name__ == "__main__":
    main()
