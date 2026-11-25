"""Sincroniza o Thaumora com o CurseForge (API oficial, chave em games/minecraft/shared/curseforge.key).

Passos:
  1. fingerprint de cada jar do lock.json -> projeto/arquivo exatos no CurseForge
  2. mods que só existem no CurseForge (lock.json -> curseforge_pendentes): acha o projeto pelo slug,
     escolhe o arquivo 1.21.1 NeoForge (respeitando "pin"), segue as dependências obrigatórias e baixa
  3. grava data/cf_lock.json e mostra o que NÃO está no CurseForge (bloqueia a publicação)

Uso:
  python -I tools/cf_sync.py              sincroniza (passos 1-3)
  python -I tools/cf_sync.py --export     também gera dist/Thaumora-<versão>.zip (formato de modpack do CurseForge)
  python -I tools/cf_sync.py --export-only  só gera o .zip a partir do data/cf_lock.json, sem chave da API
                                           (para quando o cf_lock já está em dia com o lock.json)

A chave nunca é gravada em nenhum arquivo do pack.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT.parent.parent
CACHE = GAMES / "shared" / "mod-cache"
KEY_FILE = GAMES / "shared" / "curseforge.key"
LOCK = ROOT / "data" / "lock.json"
MODS = ROOT / "data" / "mods.json"
CF_LOCK = ROOT / "data" / "cf_lock.json"
PACK = json.loads((ROOT / "data" / "pack.json").read_text(encoding="utf-8"))
JAVA = Path(os.environ.get("APPDATA", "")) / "PrismLauncher/java/java-runtime-delta/bin/java.exe"
API = "https://api.curseforge.com"
GAME_ID, CLASS_MODS, NEOFORGE = 432, 6, 6
MC = PACK["minecraft"]
RELEASE_RANK = {1: 0, 2: 1, 3: 2}  # 1 release, 2 beta, 3 alpha
REQUIRED = 3                         # relationType de dependência obrigatória


def api_key():
    k = os.environ.get("CF_API_KEY") or (KEY_FILE.read_text(encoding="utf-8").strip() if KEY_FILE.exists() else "")
    if not k:
        sys.exit(f"Chave do CurseForge não encontrada. Salve em {KEY_FILE} ou na variável CF_API_KEY.")
    return k


KEY = None


def call(path, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"x-api-key": KEY, "Accept": "application/json",
                                          "Content-Type": "application/json",
                                          "User-Agent": "thaumora-modpack-builder/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                sys.exit(f"CurseForge recusou a chave (HTTP {e.code}). Confira o arquivo {KEY_FILE}.")
            if e.code == 404:
                return None
            time.sleep(2 + attempt * 3)
        except Exception:
            time.sleep(2 + attempt * 3)
    raise RuntimeError(f"falhou: {path}")


def fingerprints(paths):
    out, chunk = {}, 60
    for i in range(0, len(paths), chunk):
        res = subprocess.run([str(JAVA), str(ROOT / "tools" / "Murmur2.java"), *map(str, paths[i:i + chunk])],
                             capture_output=True, text=True, check=True)
        for line in res.stdout.splitlines():
            fp, p = line.split("\t", 1)
            out[Path(p).name] = int(fp)
    return out


def best_file(mod_id, pin=None):
    q = urllib.parse.urlencode({"gameVersion": MC, "modLoaderType": NEOFORGE, "pageSize": 50})
    files = (call(f"/v1/mods/{mod_id}/files?{q}") or {}).get("data", [])
    if pin:
        return next((f for f in files if pin in f["fileName"] or pin in f.get("displayName", "")), None)
    files = [f for f in files if MC in f.get("gameVersions", [])]
    return min(files, key=lambda f: (RELEASE_RANK.get(f["releaseType"], 3), -int(f["id"]))) if files else None


def download(f):
    dest = CACHE / f["fileName"]
    sha1 = next((h["value"] for h in f.get("hashes", []) if h["algo"] == 1), None)
    if dest.exists() and (not sha1 or hashlib.sha1(dest.read_bytes()).hexdigest() == sha1):
        return "cache"
    if not f.get("downloadUrl"):
        return "manual"  # o autor não libera download por apps de terceiros: baixar no site
    with urllib.request.urlopen(urllib.request.Request(f["downloadUrl"], headers={"User-Agent": "thaumora"}), timeout=180) as r:
        data = r.read()
    if sha1 and hashlib.sha1(data).hexdigest() != sha1:
        raise RuntimeError(f"sha1 não confere: {f['fileName']}")
    dest.write_bytes(data)
    return "baixado"


def main():
    global KEY
    if "--export-only" in sys.argv:
        return export_only()
    KEY = api_key()
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    pins = {m["cf"]: m["pin"] for m in json.loads(MODS.read_text(encoding="utf-8")) if m.get("cf") and m.get("pin")}

    # 1. fingerprint dos jars do Modrinth
    jars = [CACHE / m["file"] for m in lock["mods"]]
    fps = fingerprints(jars)
    res = call(f"/v1/fingerprints/{GAME_ID}", {"fingerprints": list(fps.values())})["data"]
    by_fp = {m["file"]["fileFingerprint"]: m for m in res.get("exactMatches", [])}
    entries, missing = [], []
    for m in lock["mods"]:
        hit = by_fp.get(fps[m["file"]])
        if hit:
            entries.append({"n": m["title"], "projectID": hit["id"], "fileID": hit["file"]["id"],
                            "file": m["file"], "origem": "modrinth", "client": m["client"], "server": m["server"]})
        else:
            missing.append({"n": m["title"], "mr": m["slug"], "file": m["file"]})
    have = {e["projectID"] for e in entries}
    print(f"fingerprint: {len(entries)} de {len(lock['mods'])} jars achados no CurseForge")

    # 2. mods que só existem no CurseForge (+ dependências obrigatórias)
    queue = [(c["cf"], c["n"]) for c in lock.get("curseforge_pendentes", [])]
    manual, notfound = [], []
    while queue:
        ref, why = queue.pop(0)
        if isinstance(ref, int):
            mod_id, slug = ref, None
        else:
            q = urllib.parse.urlencode({"gameId": GAME_ID, "classId": CLASS_MODS, "slug": ref})
            found = (call(f"/v1/mods/search?{q}") or {}).get("data", [])
            if not found:  # slug errado: sugere candidatos pelo nome (corrigir "cf" em mods.json)
                q = urllib.parse.urlencode({"gameId": GAME_ID, "classId": CLASS_MODS, "searchFilter": why.split("/")[0],
                                            "gameVersion": MC, "modLoaderType": NEOFORGE, "pageSize": 5})
                sug = [f"{p['name']} = {p['slug']}" for p in (call(f"/v1/mods/search?{q}") or {}).get("data", [])]
                notfound.append(f"{why} (slug '{ref}') — candidatos: {'; '.join(sug) or 'nenhum'}")
                continue
            mod_id, slug = found[0]["id"], ref
        if mod_id in have:
            continue
        f = best_file(mod_id, pins.get(slug))
        if not f:
            notfound.append(f"{why}: sem arquivo {MC} NeoForge")
            continue
        have.add(mod_id)
        st = download(f)
        if st == "manual":
            site = call(f"/v1/mods/{mod_id}")["data"]["links"]["websiteUrl"]
            manual.append({"n": why, "file": f["fileName"], "url": f"{site}/files/{f['id']}"})
        entries.append({"n": why, "projectID": mod_id, "fileID": f["id"], "file": f["fileName"], "origem": "curseforge"})
        for d in f.get("dependencies", []):
            if d["relationType"] == REQUIRED and d["modId"] not in have:
                queue.append((d["modId"], f"dependência de {why}"))

    # nomes reais das dependências achadas por ID
    ids = [e["projectID"] for e in entries if e["n"].startswith("dependência de")]
    if ids:
        names = {p["id"]: p["name"] for p in call("/v1/mods", {"modIds": ids})["data"]}
        for e in entries:
            if e["projectID"] in names and e["n"].startswith("dependência de"):
                e["via"], e["n"] = e["n"], names[e["projectID"]]

    CF_LOCK.write_text(json.dumps({"minecraft": MC, "neoforge": PACK["neoforge"], "files": entries,
                                   "fora_do_curseforge": missing, "download_manual": manual,
                                   "nao_encontrados": notfound}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"só CurseForge: {sum(e['origem'] == 'curseforge' for e in entries)} (com dependências)")
    for x in notfound:
        print("  ? não achado:", x)
    for x in manual:
        print(f"  ↓ baixar à mão (autor bloqueia apps): {x['n']} -> {x['url']}")
    print(f"\nFORA do CurseForge ({len(missing)}): bloqueiam a publicação até trocar ou remover")
    for x in missing:
        print(f"  ✗ {x['n']} ({x['file']})")

    if "--export" in sys.argv:
        export(entries, missing)


def export_only():
    """Gera o .zip a partir do cf_lock.json, conferindo antes se ele cobre exatamente os jars do pack."""
    cf = json.loads(CF_LOCK.read_text(encoding="utf-8"))
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    prism = ROOT / "data" / "cf_prism.json"
    pack_files = {m["file"] for m in lock["mods"]}
    if prism.exists():
        pack_files |= {c["file"] for c in json.loads(prism.read_text(encoding="utf-8"))["files"]}
    cf_files = {e["file"] for e in cf["files"]}
    if pack_files != cf_files:
        print("O cf_lock.json está desatualizado em relação ao lock.json/cf_prism.json:")
        for f in sorted(pack_files - cf_files):
            print("  sem ID no CurseForge:", f)
        for f in sorted(cf_files - pack_files):
            print("  não está mais no pack:", f)
        sys.exit("Atualize o cf_lock.json (cf_sync.py com a chave, ou à mão) antes de exportar.")
    export(cf["files"], cf.get("fora_do_curseforge", []))


def export(entries, missing):
    if missing:
        print("\n(atenção: o .zip sai sem os mods acima, que não estão no CurseForge)")
    manifest = {
        "minecraft": {"version": MC, "modLoaders": [{"id": f"neoforge-{PACK['neoforge']}", "primary": True}],
                      **({"recommendedRam": PACK["ram_mb"]} if PACK.get("ram_mb") else {})},
        "manifestType": "minecraftModpack", "manifestVersion": 1,
        "name": PACK["name"], "version": PACK["version"], "author": PACK["author"],
        "files": [{"projectID": e["projectID"], "fileID": e["fileID"], "required": True} for e in entries],
        "overrides": "overrides",
    }
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    out = dist / f"{PACK['name']}-{PACK['version']}.zip"
    modlist = "<ul>\n" + "\n".join(f"<li>{e['n']}</li>" for e in sorted(entries, key=lambda e: e["n"].lower())) + "\n</ul>\n"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        z.writestr("modlist.html", modlist)
        ov = ROOT / "overrides"  # configs, kubejs, quests etc. que vão junto no pack
        if ov.exists():
            for p in sorted(ov.rglob("*")):
                if p.is_file() and not any(part.startswith(".") for part in p.relative_to(ov).parts):
                    z.write(p, "overrides/" + p.relative_to(ov).as_posix())
    print(f"\nmodpack gerado: {out} ({len(entries)} mods)")


if __name__ == "__main__":
    main()
