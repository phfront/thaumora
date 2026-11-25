"""Monta a pasta de mods de uma instância do Prism a partir de data/lock.json e data/cf_prism.json.

O que faz:
  - copia para a instância todo jar do lock (Modrinth) e do cf_prism (CurseForge) que estiver faltando,
    pegando do cache (../../shared/mod-cache) ou baixando se não estiver lá;
  - troca jars com sha1 diferente do esperado;
  - tira da instância os jars que não estão em nenhum dos dois arquivos (vão para
    .minecraft/mods-removidos/<data>/, nada é apagado);
  - mantém os arquivos mods/.index/*.pw.toml do Prism em dia para os mods do CurseForge;
  - guarda no cache uma cópia de cada jar do CurseForge, para o cache ter o pack inteiro.

A instância precisa de TODOS os mods do lock, inclusive os "só servidor": o singleplayer roda um servidor interno.

Uso:
  python -I tools/build_instance.py                 só mostra o que faria (não mexe em nada)
  python -I tools/build_instance.py --apply         aplica as mudanças (feche o jogo antes)
  python -I tools/build_instance.py --import-prism  regrava data/cf_prism.json a partir de mods/.index da instância
                                                    (use depois de instalar um mod do CurseForge pelo Prism)
Opções:
  --instance <pasta>   instância do Prism (padrão: %APPDATA%/PrismLauncher/instances/Thaumora)
  --no-download        não baixa nada; só usa o cache e a própria instância
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
import tomllib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "data" / "lock.json"
CF_PRISM = ROOT / "data" / "cf_prism.json"
CACHE = ROOT.parent.parent / "shared" / "mod-cache"
UA = {"User-Agent": "thaumora-modpack-builder/1.0"}
DEFAULT_INSTANCE = Path(os.environ.get("APPDATA", "")) / "PrismLauncher" / "instances" / "Thaumora"
CF_COMMENT = ("Mods instalados pelo Prism a partir do CurseForge (IDs para o manifest.json). "
              "Gerado de mods/.index da instância por tools/build_instance.py --import-prism.")


def sha1_of(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def arg_value(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        sys.exit(f"faltou o valor de {name}")
    return None


def mods_dir_of(instance):
    for sub in (".minecraft", "minecraft"):
        d = instance / sub / "mods"
        if d.is_dir():
            return d
    sys.exit(f"pasta de mods não encontrada em {instance}")


def cf_url(entry):
    """URL pública do arquivo no CDN do CurseForge (não precisa de chave da API)."""
    # o nome que o CDN aceita é o que o Prism salvou na pasta de mods (testado: "+" e maiúsculas do
    # nome original dão 403)
    fid = str(entry["fileID"])
    return f"https://mediafilez.forgecdn.net/files/{fid[:-3]}/{int(fid[-3:])}/{urllib.request.quote(entry['file'])}"


def expected_files():
    """file -> {sha1, urls, source, name, (cf)}: tudo que a pasta de mods deve ter."""
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    want = {}
    for m in lock["mods"]:
        want[m["file"]] = {"sha1": m["sha1"], "urls": [m["url"]], "source": "modrinth", "name": m["title"]}
    if CF_PRISM.exists():
        for c in json.loads(CF_PRISM.read_text(encoding="utf-8"))["files"]:
            if c["file"] in want:
                print(f"  ! {c['file']} está no lock e no cf_prism; vale o do lock")
                continue
            want[c["file"]] = {"sha1": c["sha1"], "urls": [cf_url(c)], "source": "curseforge", "name": c["n"], "cf": c}
    return want


def read_index(mods_dir):
    """Arquivos .pw.toml do Prism: nome do jar -> (caminho do toml, conteúdo)."""
    out = {}
    idx = mods_dir / ".index"
    if idx.is_dir():
        for t in sorted(idx.glob("*.pw.toml")):
            try:
                data = tomllib.loads(t.read_text(encoding="utf-8"))
            except tomllib.TOMLDecodeError as e:
                print(f"  ! não consegui ler {t.name}: {e}")
                continue
            out[data.get("filename", "")] = (t, data)
    return out


def import_prism(mods_dir):
    files = []
    for fname, (path, data) in read_index(mods_dir).items():
        if data.get("download", {}).get("mode") != "metadata:curseforge":
            continue
        cf = data.get("update", {}).get("curseforge", {})
        entry = {"n": data.get("name", fname), "file": fname, "projectID": cf.get("project-id"),
                 "fileID": cf.get("file-id"), "sha1": data["download"]["hash"],
                 "index": path.name[: -len(".pw.toml")]}
        if not (mods_dir / fname).exists():
            print(f"  ! {fname}: tem .pw.toml mas o jar não está na pasta de mods (ignorado)")
            continue
        files.append(entry)
    files.sort(key=lambda e: e["n"].lower())
    old = json.loads(CF_PRISM.read_text(encoding="utf-8"))["files"] if CF_PRISM.exists() else []
    old_files, new_files = {e["file"] for e in old}, {e["file"] for e in files}
    CF_PRISM.write_text(json.dumps({"_comentario": CF_COMMENT, "files": files}, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    print(f"cf_prism.json: {len(files)} mods do CurseForge")
    for f in sorted(new_files - old_files):
        print("  + entrou:", f)
    for f in sorted(old_files - new_files):
        print("  - saiu:", f)


def toml_text(c):
    s = json.dumps  # string básica do TOML aceita os mesmos escapes do JSON
    return (f"filename = {s(c['file'])}\nname = {s(c['n'])}\nside = 'both'\n"
            "x-prismlauncher-loaders = [ 'neoforge' ]\nx-prismlauncher-mc-versions = [ '1.21.1' ]\n"
            f"x-prismlauncher-release-type = 'release'\nx-prismlauncher-version-number = {s(c['file'])}\n\n"
            f"[download]\nhash = {s(c['sha1'])}\nhash-format = 'sha1'\nmode = 'metadata:curseforge'\nurl = ''\n\n"
            f"[update.curseforge]\nfile-id = {int(c['fileID'])}\nproject-id = {int(c['projectID'])}\n")


def index_name(c):
    return c.get("index") or re.sub(r"[^a-z0-9]+", "-", c["n"].lower()).strip("-")


def fetch(fname, info, mods_dir, download):
    """Garante o jar certo no cache e devolve o caminho dele (ou None)."""
    cached = CACHE / fname
    if cached.exists() and sha1_of(cached) == info["sha1"]:
        return cached
    here = mods_dir / fname
    if here.exists() and sha1_of(here) == info["sha1"]:
        CACHE.mkdir(parents=True, exist_ok=True)
        shutil.copy2(here, cached)
        return cached
    if not download:
        return None
    for url in info["urls"]:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                data = r.read()
        except Exception as e:
            print(f"  ! falhou o download de {fname}: {e}")
            continue
        if hashlib.sha1(data).hexdigest() != info["sha1"]:
            print(f"  ! sha1 não confere no download de {fname}")
            continue
        CACHE.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(data)
        return cached
    return None


def move_aside(path, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / path.name
    n = 2
    while target.exists():
        target = dest_dir / f"{path.stem}.{n}{path.suffix}"
        n += 1
    shutil.move(str(path), str(target))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    instance =Path(arg_value("--instance") or DEFAULT_INSTANCE)
    mods_dir = mods_dir_of(instance)
    if "--import-prism" in sys.argv:
        import_prism(mods_dir)
        return

    apply, download = "--apply" in sys.argv, "--no-download" not in sys.argv
    want = expected_files()
    present = {p.name: p for p in mods_dir.glob("*.jar")}
    index = read_index(mods_dir)

    ok, missing, wrong = [], [], []
    for fname, info in want.items():
        if fname not in present:
            missing.append(fname)
        elif sha1_of(present[fname]) != info["sha1"]:
            wrong.append(fname)
        else:
            ok.append(fname)
    extra = sorted(f for f in present if f not in want)
    cf_want = {f: i["cf"] for f, i in want.items() if i["source"] == "curseforge"}
    toml_missing = sorted(f for f in cf_want if f not in index)
    toml_orphan = sorted(f for f, (p, _) in index.items() if f not in want)
    disabled = sorted(p.name for p in mods_dir.glob("*.disabled"))

    n_mr = sum(1 for i in want.values() if i["source"] == "modrinth")
    print(f"instância: {mods_dir}")
    print(f"esperado: {len(want)} jars ({n_mr} do Modrinth + {len(cf_want)} do CurseForge) | na pasta: {len(present)}")
    print(f"ok: {len(ok)} | faltam: {len(missing)} | sha1 diferente: {len(wrong)} | sobrando: {len(extra)}")
    for title, items in (("faltam", missing), ("sha1 diferente (troca)", wrong), ("sobrando (sai da instância)", extra),
                         (".pw.toml faltando (cria)", toml_missing), (".pw.toml sem mod (sai)", toml_orphan),
                         ("desativados no Prism (não mexo)", disabled)):
        if items:
            print(f"\n{title}:")
            for f in items:
                print("  -", f)

    if not apply:
        if missing or wrong or extra or toml_missing or toml_orphan:
            print("\nNada foi alterado. Rode de novo com --apply para aplicar (com o jogo fechado).")
        else:
            print("\nA instância já está igual ao lock.")
        return

    removed_dir = mods_dir.parent / "mods-removidos" / datetime.date.today().isoformat()
    failed = []
    for fname in extra + wrong:
        move_aside(mods_dir / fname, removed_dir)
    for fname in missing + wrong:
        src = fetch(fname, want[fname], mods_dir, download)
        if src is None:
            failed.append(fname)
            continue
        shutil.copy2(src, mods_dir / fname)
    for fname in toml_orphan:
        move_aside(index[fname][0], removed_dir / ".index")
    (mods_dir / ".index").mkdir(exist_ok=True)
    for fname in toml_missing:
        c = cf_want[fname]
        (mods_dir / ".index" / f"{index_name(c)}.pw.toml").write_text(toml_text(c), encoding="utf-8")
    for fname in cf_want:  # cache com o pack inteiro, inclusive o que veio do CurseForge
        if fname not in failed:
            fetch(fname, want[fname], mods_dir, download=False)

    print(f"\naplicado. Removidos foram para {removed_dir}" if (extra or wrong or toml_orphan) else "\naplicado.")
    if failed:
        print("não consegui obter (instale pelo Prism ou rode sem --no-download):")
        for f in failed:
            print("  -", f)
        sys.exit(1)


if __name__ == "__main__":
    main()
