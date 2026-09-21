"""
Meridian OpsConsole — Machine A (network vulnerability: plaintext credentials)

Plaintext TCP admin console on port 2222. Intentionally insecure -- no TLS,
no rate limiting. DO NOT deploy this anywhere internet-facing outside the
controlled CTF network.
"""

import socketserver

USERS = {
    "ops_svc": ("N3twork_Ops_2026!", "ops"),
    "sysadmin": ("R00tR0b0tics#99", "admin"),
}


class OpsConsoleHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b"Meridian OpsConsole v1.2\r\n")

        self.wfile.write(b"username: ")
        username = self.rfile.readline().decode(errors="replace").strip()

        self.wfile.write(b"password: ")
        password = self.rfile.readline().decode(errors="replace").strip()

        record = USERS.get(username)
        if record is None or record[0] != password:
            self.wfile.write(b"Access denied.\r\n")
            return

        role = record[1]
        self.wfile.write(f"Welcome, {username} ({role}).\r\n".encode())
        self.wfile.write(b"> ")
        command = self.rfile.readline().decode(errors="replace").strip()

        if command == "status":
            if role == "admin":
                self.wfile.write(
                    b"All systems nominal. Reminder: ticket MRB-7E42D9 still "
                    b"open (ops_svc credential rotation).\r\n"
                    b"FLAG{2nd_flA6_ARP_D0wN_g00d_stuff}\r\n"
                )
            else:
                self.wfile.write(b"All systems nominal.\r\n")
        else:
            self.wfile.write(b"Unknown command.\r\n")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    server = ThreadedTCPServer(("0.0.0.0", 2222), OpsConsoleHandler)
    server.serve_forever()
