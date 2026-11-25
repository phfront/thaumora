"""Serve as páginas dos projetos de Minecraft só na interface do Tailscale.

- GET /            -> modpacks/thaumora/thaumora.html
- GET /thaumind    -> mods/thaumind/docs/plano.html (planejamento do mod Thaumind)
- GET /__version   -> data de modificação das páginas (elas usam para se recarregar sozinhas)

Sempre lê a versão atual do disco, sem cache.
Uso: pythonw tools/serve.py   (roda em segundo plano; iniciado no logon pela
tarefa agendada "Thaumora Page Server"). Porta 8791 (a 8787 é usada por outro projeto).
"""
import socket
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
MINECRAFT = PACK.parent.parent
PAGES = {
    "/": PACK / "thaumora.html",
    "/index.html": PACK / "thaumora.html",
    "/thaumora.html": PACK / "thaumora.html",
    "/thaumind": MINECRAFT / "mods" / "thaumind" / "docs" / "plano.html",
    "/thaumind/": MINECRAFT / "mods" / "thaumind" / "docs" / "plano.html",
}
PORT = 8791


def tailscale_ip():
    try:
        out = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=10,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        ip = out.stdout.strip().splitlines()[0].strip() if out.stdout.strip() else ""
        socket.inet_aton(ip)
        return ip
    except Exception:
        return None


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, ctype: str):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        page = PAGES.get(path)
        if page and page.exists():
            self._send(page.read_bytes(), "text/html; charset=utf-8")
        elif path == "/__version":
            v = "-".join(str(p.stat().st_mtime_ns) for p in sorted(set(PAGES.values())) if p.exists())
            self._send(v.encode(), "text/plain")
        else:
            self.send_error(404)

    do_HEAD = do_GET

    def log_message(self, *args):
        pass


def main():
    ip = tailscale_ip()
    while ip is None:  # espera o Tailscale subir depois do logon
        time.sleep(15)
        ip = tailscale_ip()
    ThreadingHTTPServer((ip, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
