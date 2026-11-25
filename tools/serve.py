"""Serve a página do Thaumora só na interface do Tailscale.

- GET /            -> thaumora.html (sempre a versão atual do disco, sem cache)
- GET /__version   -> data de modificação do arquivo (a página usa para se recarregar sozinha)

Uso: pythonw tools/serve.py   (roda em segundo plano; iniciado no logon pela
tarefa agendada "Thaumora Page Server"). Porta 8791 (a 8787 é usada por outro projeto).
"""
import socket
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "thaumora.html"
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
        if path in ("/", "/index.html", "/thaumora.html"):
            self._send(PAGE.read_bytes(), "text/html; charset=utf-8")
        elif path == "/__version":
            self._send(str(PAGE.stat().st_mtime_ns).encode(), "text/plain")
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
