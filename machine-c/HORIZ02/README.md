# HORIZ-02 — Insecure Direct Object Reference (IDOR)

## Category
Horizontal privilege escalation

## Objective
View another analyst's profile (`analyst2`, user id 2) while authenticated only
as `analyst1` (user id 1).

## Vulnerability
The `/profile/<user_id>` route checks that a user is logged in, but never checks
that the requested object belongs to the current session. Any authenticated user
can substitute another user's id and read their record — a classic IDOR.

## Service
Flask app on TCP port 5000. Session-based login; profiles served at
`/profile/<int:user_id>`.

## Chain position
Credentials for `analyst1` are **not** given here — they are recovered from the
NET-02 anonymous rsync leak (`network-backup.txt`). Reading `analyst2`'s record
via the IDOR then leaks the `ctfuser` SSH foothold used by VERT-02.

`NET-02 (rsync) → HORIZ-02 (this) → VERT-02 (SUID root)`

## Intended Technique
1. Log in as `analyst1` using the credentials recovered from NET-02.
2. Observe your own profile URL is `/profile/1`.
3. Change the object reference in the URL to `/profile/2`.
4. The server returns `analyst2`'s profile with no ownership check.
5. Read the note field to recover the HORIZ-02 flag **and** the `ctfuser`
   SSH credentials that feed VERT-02.

## Flag
CITS3006{HORIZ02_IDOR_OBJECT}
