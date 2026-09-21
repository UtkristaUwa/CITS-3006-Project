"""
Simulated legitimate admin traffic against OpsConsole (server.py) -- without
this there's nothing on the wire for a sniffing player to capture.

Uses raw recv()/sendall(), not readline(): OpsConsole's prompts aren't
newline-terminated. _read_until() drains each prompt fully rather than
trusting a single recv(), since TCP can split one wfile.write() across
multiple reads.
"""

import socket
import time

HOST = "127.0.0.1"
PORT = 2222

INTERVAL_SECONDS = 20


def _read_until(sock, marker):
    buf = b""
    while not buf.endswith(marker):
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf


def check_in():
    with socket.create_connection((HOST, PORT), timeout=5) as sock:
        _read_until(sock, b"username: ")
        sock.sendall(b"sysadmin\r\n")

        _read_until(sock, b"password: ")
        sock.sendall(b"R00tR0b0tics#99\r\n")

        _read_until(sock, b"> ")
        sock.sendall(b"status\r\n")

        response = sock.recv(4096)
        return response


if __name__ == "__main__":
    while True:
        check_in()
        time.sleep(INTERVAL_SECONDS)
