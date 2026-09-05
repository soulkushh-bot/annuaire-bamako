"""Petit serveur de développement qui interdit toute mise en cache.
Sans cela, le navigateur garde app.js et styles.css et l'on teste une version périmée.

Usage : python scripts/serve.py [port]
"""
import http.server, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

class NoCache(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()
    def log_message(self, *a):
        pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8123
    print(f"http://127.0.0.1:{port}  (sans cache — Ctrl+C pour arrêter)")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), NoCache).serve_forever()
