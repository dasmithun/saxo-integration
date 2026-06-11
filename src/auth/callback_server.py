import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class CallbackHandler(BaseHTTPRequestHandler):
    auth_code = None
    error     = None

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "code" in params:
            CallbackHandler.auth_code = params["code"][0]
            self._respond("✅ Login successful! You can close this tab.")
        elif "error" in params:
            CallbackHandler.error = params["error"][0]
            self._respond("❌ Login failed: " + CallbackHandler.error)
        else:
            self._respond("⚠ Unexpected callback.")

    def _respond(self, message):
        body = f"<h2>{message}</h2>".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # silence server logs


def wait_for_auth_code(port=8080, timeout=120):
    CallbackHandler.auth_code = None
    CallbackHandler.error     = None

    server = HTTPServer(("localhost", port), CallbackHandler)
    server.timeout = timeout

    # Run in background thread
    thread = threading.Thread(target=server.handle_request)
    thread.start()
    thread.join(timeout=timeout)
    server.server_close()

    if CallbackHandler.error:
        raise Exception(f"OAuth error: {CallbackHandler.error}")
    if not CallbackHandler.auth_code:
        raise Exception("Timed out waiting for auth code")

    return CallbackHandler.auth_code