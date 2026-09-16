# Machine A — Meridian Robotics Dev Portal

CITS3006 CTF project — Machine A, owned by aki. All five required vuln
categories are now built: the **web vulnerability (IDOR)**, the **network
vulnerability (ARP spoofing → plaintext credential sniffing)**, the
**horizontal privilege escalation** path, the **vertical privilege
escalation** path, and the **reverse-engineering vulnerability**. See
"Still to do" at the bottom for what's left (mostly hardening/cleanup, not
new vulns).

## Theme

Machine A is the public-facing dev/staging server for the fictional company
Meridian Robotics — an internal ticketing portal engineers use to file build
and IT support tickets.

## Setup

```bash
cd machine-a
pip install -r requirements.txt --break-system-packages   # or use a venv
python3 init_db.py                                        # (re)seeds portal.db
python3 app.py                                             # runs on 0.0.0.0:5000
```

Seeded accounts:

| Username | Password | Role |
|---|---|---|
| jchen | Summer2024! | developer |
| mfoster | P@ssword2024 | developer |
| sysadmin | R00tR0b0tics#99 | admin |

`jchen` is the account a participant would plausibly start with (e.g. handed
out at the start of the challenge, or discovered via a separate weak-auth /
recon step you can build in later). `sysadmin`'s password is intentionally
not meant to be guessed — it's not the intended path in.

## The vulnerability: IDOR

`GET /ticket/<ref>` fetches a ticket purely by the opaque ref string in the
URL. It never checks that the ticket actually belongs to the logged-in user
(`tickets.user_id == session['user_id']`). See the comment block in
`app.py` above `view_ticket()`.

Every user's own tickets only ever link to their own refs from `/dashboard`.
The `/activity` page (linked in the nav as "Team Activity") is a separate,
unscoped feature that lists all 8 ticket refs and who opened them, for every
logged-in user regardless of role — that's where the target ref is found.
It doesn't link to the tickets themselves, so reaching one still requires
manually editing the URL to `/ticket/<ref>`.

## Sample solution (intended solve path)

1. Log in as `jchen` / `Summer2024!`.
2. On `/dashboard`, note your own tickets (three refs) — nothing from
   `sysadmin`.
3. Open **Team Activity** (`/activity`) — see all 8 entries, including two
   opened by `sysadmin`: `MRB-2D9A88` and `MRB-7E42D9`.
4. Try `/ticket/MRB-2D9A88` first (the more recent-looking one) → a boring
   decoy, "Firewall rule cleanup - low priority." Dead end.
5. Try `/ticket/MRB-7E42D9` → belongs to `sysadmin`: **"Rotate ops_svc
   credentials before audit."** This discloses:
   - `ops_svc` credentials (`ops_svc / N3twork_Ops_2026!`) for a service on
     port 2222 on the ops/build host — this is the intended feed into the
     **network vulnerability** and the **horizontal PE** path below.
   - The flag: `FLAG{idor_tickets_leak_ops_creds}`

   Note: an earlier draft also disclosed the `sysadmin` SSH key passphrase
   directly in this ticket. That was deliberately removed — reaching
   vertical PE now requires having already solved horizontal PE first (see
   below), rather than letting the IDOR alone shortcut straight to root.
   Piling every downstream secret behind one disclosure would have read as
   one vulnerability wearing three flags rather than a real chain.

No automated scanner solves this by default: there's no sequential ID space
to brute-force (refs are opaque, non-sequential strings), and reaching the
real ticket requires finding a secondary page (`/activity`) and manually
disambiguating it from a decoy (`MRB-2D9A88`) — not just fuzzing integers.
This satisfies the unit's "not solvable by automated tools alone" difficulty
bar.

## The network vulnerability: ARP spoofing → plaintext credential sniffing

`ops-console/server.py` is a second, independent service — a plaintext TCP
admin console (`OpsConsole`) on port 2222, unrelated to the Flask app. It
has no TLS. On a switched LAN that alone isn't exploitable by just running
Wireshark: a switch only forwards a host's traffic to that host, so a
passive listener on a third machine sees nothing of the OpsConsole↔admin
conversation. The actual vulnerability is that the network has no
protection against ARP spoofing (no dynamic ARP inspection, no static ARP
entries, no port security), which lets an attacker forge ARP replies to
insert themselves as a transparent man-in-the-middle between OpsConsole and
whoever's talking to it — at which point the plaintext protocol becomes
readable.

`ops-console/healthcheck_client.py` simulates that legitimate admin traffic:
it logs into OpsConsole as `sysadmin` and runs `status` every
`INTERVAL_SECONDS` (20s by default). Without it there'd be nothing for a
positioned attacker to actually capture.

This was validated end-to-end in a 3-host simulated LAN (Machine A, a
monitoring host, an attacker), bridged together like a real switch:

- **Baseline (no spoofing):** the attacker's capture showed zero packets of
  the monitor↔Machine A conversation, confirming switch isolation is real —
  passive sniffing alone doesn't work.
- **With `arpspoof` run bidirectionally** (real `dsniff` tool) plus IP
  forwarding enabled on the attacker: Machine A's ARP table ended up
  mapping the monitor's IP to the attacker's MAC; the monitor↔Machine A
  connection still completed normally (proving transparent MITM, not a
  DoS); and the attacker's capture caught the `sysadmin` /
  `R00tR0b0tics#99` login, plus the `status` response, in cleartext.

### Sample solution (network vuln)

1. Position as MITM between OpsConsole and its legitimate traffic via ARP
   spoofing (e.g. `arpspoof` in both directions + IP forwarding).
2. Passively capture a `healthcheck_client.py` check-in cycle (occurs every
   20s) — this discloses the `sysadmin` OpsConsole login in plaintext
   (`sysadmin` / `R00tR0b0tics#99`), a credential never leaked anywhere else
   in the game (unlike `ops_svc`'s password, which is disclosed via the web
   IDOR).
3. The captured `status` response for the `sysadmin` (admin) session
   contains: `FLAG{arp_spoof_opsconsole_sysadmin_sniff}`.

Because the flag only ever appears in traffic gated behind the `sysadmin`
OpsConsole login, and that password is never disclosed by any other path,
actually ARP-spoofing and sniffing is the only way to get it — not
something obtainable via the web app or brute force.

## The horizontal privilege escalation: ops_svc → build (group misconfig)

Unlike the two vulns above, this one lives at the OS level on the real
Machine A VM, not inside a simulated Python service — horizontal PE only
makes sense against a real multi-user box with real accounts. Provisioning
lives in `provision_horizontal_pe.sh`; run it once as root on the actual VM
before shipping.

`ops_svc`'s credentials (leaked via the IDOR above) are also its real SSH
login on Machine A — the same password-reuse pattern as `sysadmin`'s
OpsConsole/web-login reuse in the network vuln. Once logged in as `ops_svc`,
`id` reveals an unexpected secondary group: `deploy`. That group also
contains a second service account, `build`, and — this is the actual
misconfiguration — `build`'s SSH private key at `/srv/build/.ssh/id_ed25519`
is mode `640`, group `deploy`, so `ops_svc` can read it despite not owning
it. Reading the key lets `ops_svc` SSH straight in as `build`.

In-universe justification: `build`'s permissions problem is the same one
referenced in jchen's very first ticket, `MRB-1A2B3C` ("Staging build
pipeline failing... permissions error writing to `/srv/build`") — sysadmin
temporarily added `ops_svc` to the `deploy` group to help debug that
Jenkins job, fixed the actual bug, and forgot to revoke the group
membership. Players who remember that early, easy-to-skip ticket get a
"click" moment; players who don't can still find it by just enumerating
what the unexpected `deploy` group grants access to.

Both `ops_svc` and `build` are unprivileged service accounts with no sudo
rights — this is a lateral move to a same-privilege-level account, not an
escalation to root. `/srv/build` also has ordinary decoy clutter
(`deploy.sh`, `build.log`) so the directory listing alone doesn't point
straight at `.ssh`.

### Sample solution (horizontal PE)

1. SSH to Machine A as `ops_svc` using the IDOR-leaked creds:
   `ssh ops_svc@<machine-a-ip>` (password `N3twork_Ops_2026!`).
2. `id` → notice the extra group: `ops_svc deploy`.
3. `find /srv/build -group deploy 2>/dev/null` → turns up
   `/srv/build/.ssh/id_ed25519` (mode 640, owner `build:deploy`).
4. `cat` it out, `chmod 600` a local copy, then
   `ssh -i <key> build@<machine-a-ip>`.
5. `cat ~/flag_horizontal.txt` → `FLAG{horizontal_ops_svc_group_perms_to_build}`

Not automatable by a generic scanner: it requires already holding
`ops_svc`'s creds (only obtainable via the IDOR chain), noticing an
unexpected secondary group, and connecting that group to a specific path
the game only hinted at via an old ticket.

## The vertical privilege escalation: sysadmin backup archive → sudo → root

Like horizontal PE, this lives at the OS level. Provisioning is in
`provision_vertical_pe.sh` — run it once as root, **after**
`provision_horizontal_pe.sh` (it depends on the `build` user and
`/srv/build` already existing).

Once an attacker has pivoted to `build` (via horizontal PE), simply
exploring `/srv/build/backups/pre-audit-2026-07-09/` — a directory `build`
already owns, no further permission bug needed — turns up three dated home
directory backups from a rushed pre-audit sweep. Two (`jchen`, `mfoster`)
are boring. The third, `sysadmin_home.tar.gz`, contains `sysadmin`'s
encrypted SSH private key plus a note (also left by `ops_svc`, same
folder) explaining the passphrase was temporarily reset to a default value
to get an automated backup-verification step to pass, and never rotated
back. `sysadmin` has real sudo rights and — deliberately — no password set
at all, so the key and its passphrase are the *only* way in.

This is the redesign point worth remembering for the report: an earlier
draft disclosed this passphrase directly via the web IDOR, which would
have let an attacker skip straight from the web vuln to root without ever
touching horizontal PE. Moving the secret into an artifact only reachable
via the `build` foothold forces the real order: web IDOR → creds →
horizontal PE → recon as `build` → vertical PE.

### Sample solution (vertical PE)

1. From the `build` shell (after horizontal PE):
   `ls -la /srv/build/backups/pre-audit-2026-07-09/`
2. Extract the real one: `tar -xzf sysadmin_home.tar.gz -C /tmp/loot`
3. Inside: `.ssh/id_ed25519` (encrypted) and `backup_notes.txt`, which
   discloses the passphrase (`M3ridian_D3v!`).
4. `ssh -i /tmp/loot/sysadmin_home/.ssh/id_ed25519 sysadmin@<machine-a-ip>`
5. `sudo cat /root/flag_vertical.txt` →
   `FLAG{vertical_sysadmin_backup_key_sudo_root}`

## The reverse-engineering vulnerability: meridian-diag crackme

Source lives at `re-challenge/meridian_diag.c` in this folder — **never**
copied onto the VM itself. `provision_re.sh` compiles it fresh (stripped,
no debug symbols) and installs the binary at `/opt/meridian-tools/`.
Independent of the PE chain on purpose: any authenticated user on the box
(even just `ops_svc`, the earliest foothold) can find and copy the binary
off to reverse-engineer entirely on their own machine, offline. This
deliberately tests a different skill (static/dynamic binary analysis)
rather than adding another rung to the same escalation ladder.

The binary is a fake "firmware diagnostic utility" that prompts for an
engineer unlock code. Both the code and the flag are stored XOR-encoded
against a hardcoded 8-byte key inside the binary — `strings` on it reveals
nothing. Reaching the flag requires actually disassembling `main` (Ghidra,
`objdump -d`, or gdb) to recover the XOR key and either compute the real
unlock code or patch the comparison to always succeed.

### Sample solution (RE)

1. From any OS foothold (e.g. `ops_svc`), find and pull the binary:
   `ls -la /opt/meridian-tools/`, then copy it to your own machine.
2. `strings meridian-diag` — nothing useful, confirming it's encoded, not
   plaintext.
3. Disassemble the comparison loop in `main`: it XORs each input byte
   against a repeating key ("Meridian" — visible as bytes
   `4d 65 72 69 64 69 61 6e`) and compares against a second hardcoded
   array.
4. XOR-decode that array against the same key to recover the real code
   (`R0b0t1cs-Eng-7734`), or just patch the post-comparison conditional
   jump so any input passes.
5. Run it: `./meridian-diag` → `FLAG{re_xor_unlock_meridian_diag}`

Not solvable by `strings`, brute force (17-char keyspace), or any web/
network scanner — this one genuinely requires binary analysis.

## Still to do

- General hardening pass on the box (this app is deliberately the *only*
  intended web vuln — don't accidentally leave the Flask debugger/PIN
  active, or other unintended holes, in the final build. `debug=True` in
  `app.py` is fine for local dev but should be turned off before this ships
  to the shared CTF network). Also confirm `ops_svc` and `build` never
  pick up sudo rights or membership in a privileged group — both
  `provision_horizontal_pe.sh` and `provision_vertical_pe.sh` sanity-check
  this at the end of their runs, but re-verify after any manual changes to
  the box.
- Run `provision_re.sh` on the VM and verify the sample solution end to
  end (same way horizontal/vertical PE were verified) before considering
  Machine A fully done.

## Notes for the report (exploit map)

**Web vulnerability — IDOR**
- Vulnerability type: Insecure Direct Object Reference (IDOR)
- Entry point: `/ticket/<ref>` (requires an authenticated low-priv session);
  refs are discovered via the unscoped `/activity` feed
- Impact: horizontal information disclosure across all users' tickets;
  discloses credentials/leads for further chained exploitation
- Flag: `FLAG{idor_tickets_leak_ops_creds}`

**Network vulnerability — ARP spoofing / no ARP-spoofing protection**
- Vulnerability type: insecure LAN — no dynamic ARP inspection, no static
  ARP entries, no port security; exploitable payoff is the plaintext
  OpsConsole protocol (`ops-console/server.py`, TCP port 2222) once
  positioned as MITM
- Entry point: ARP-spoof `OpsConsole` and its legitimate admin traffic
  (`ops-console/healthcheck_client.py`, a periodic `sysadmin` login), then
  passively capture the plaintext credentials and command output
- Impact: full credential disclosure for an account (`sysadmin`) not leaked
  anywhere else in the game; validated as a genuine transparent MITM (not a
  DoS) against a real switched-LAN simulation
- Flag: `FLAG{arp_spoof_opsconsole_sysadmin_sniff}`

**Horizontal privilege escalation — group-membership misconfiguration**
- Vulnerability type: excessive/leftover group membership granting
  unintended read access to another account's SSH private key
- Entry point: SSH as `ops_svc` (creds from the IDOR chain), enumerate the
  `deploy` group, read `build`'s group-readable private key at
  `/srv/build/.ssh/id_ed25519`
- Impact: lateral movement to a second same-privilege-level service account
  (`build`); no privilege gain over root, by design — this is horizontal,
  not vertical
- Flag: `FLAG{horizontal_ops_svc_group_perms_to_build}`

**Vertical privilege escalation — sensitive backup left in a shared directory**
- Vulnerability type: insecure storage of an encrypted credential (SSH key
  + its passphrase, both recoverable from the same backup) reachable from
  an already-compromised lower-privilege account
- Entry point: as `build` (from horizontal PE), read
  `/srv/build/backups/pre-audit-2026-07-09/sysadmin_home.tar.gz` — no
  additional permission bug needed, `build` already owns the directory —
  extract `sysadmin`'s encrypted private key and its passphrase from the
  accompanying note, then SSH in as `sysadmin`
- Impact: full escalation to root via `sysadmin`'s real sudo rights;
  strictly requires horizontal PE to already be solved, since this is the
  only place the secret exists (a deliberate redesign — an earlier draft
  leaked this passphrase via the web IDOR directly, which would have let
  vertical PE skip horizontal PE entirely)
- Flag: `FLAG{vertical_sysadmin_backup_key_sudo_root}`

**Reverse engineering — XOR-encoded crackme**
- Vulnerability type: weak/reversible obfuscation of a credential check and
  its payload inside a compiled binary (no cryptographic protection, just
  XOR against a static key)
- Entry point: `/opt/meridian-tools/meridian-diag`, world-executable;
  reachable from any OS foothold, independent of the PE chain
- Impact: recovering the encoded unlock code (or patching the check)
  requires genuine static/dynamic binary analysis — not automatable by
  `strings`, brute force, or a network/web scanner
- Flag: `FLAG{re_xor_unlock_meridian_diag}`
