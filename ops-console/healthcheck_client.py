"""
Simulated legitimate admin traffic against OpsConsole (server.py).

Without this, there's nothing for a player sniffing the network to capture
except their own connections -- this is what makes the plaintext-credential
vulnerability actually exploitable via passive capture.

Uses raw recv()/sendall(), not readline(): OpsConsole's prompts ("username: ",
"password: ", "> ") are not newline-terminated, so a readline()-based client
hangs forever waiting for a '\n' that never comes.

Each prompt is drained with _read_until(), not a single recv(): the server
writes each prompt as a separate wfile.write() call (e.g. the welcome line
and "> " are two writes back to back), and TCP gives no guarantee those
land in the same recv() on the client side. A single fixed recv() here
intermittently caught only the welcome line, silently dropping "> " and the
real status response when the connection closed (observed locally: ~40% of
check-ins). _read_until() accumulates recv()s until the expected prompt has
fully arrived, which is correct regardless of how the writes get split.
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
