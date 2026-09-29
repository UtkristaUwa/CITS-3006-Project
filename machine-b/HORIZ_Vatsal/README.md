# HORIZ-03 — JWT Forgery (weak signing secret)

## Category
Horizontal privilege escalation

## Objective
Access another analyst's profile (`analyst2`) by forging an authentication
token, without knowing that user's password.

## Vulnerability
The API issues HS256 JSON Web Tokens signed with a weak, guessable secret
(`CITS3006`). Because the same secret verifies incoming tokens, an attacker who
recovers or guesses it can mint a valid token for any user and move sideways
from one analyst account to another.

## Service
Flask API on TCP port 5000. `POST /login` returns a token; `GET /profile`
returns the profile for the `sub` claim in a `Bearer` token.

## Intended Technique
1. Log in as the low-privilege user `analyst1` and capture the returned JWT.
2. Decode the token and observe it is HS256 with claims `sub` and `role`.
3. Recover the signing secret (`CITS3006`) — e.g. by brute force / wordlist
   against the token, or by guessing the weak project-themed value.
4. Forge a new token with `"sub": "analyst2"` signed with the recovered secret.
5. Call `GET /profile` with the forged token as a `Bearer` credential.
6. Read `analyst2`'s note to recover the HORIZ-03 flag.

## Flag
CITS3006{HORIZ03_JWT_FORGERY}

## Chain
This account pivot sets up Machine B's vertical PE: the SUID program
`/usr/local/bin/ctf-vert03` loads `libctfhelper.so` from the writable
directory `/opt/vert03/lib` — see **VERT-03**.
