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

## Intended Technique
1. Log in with the provided low-privilege credentials for `analyst1`.
2. Observe your own profile URL is `/profile/1`.
3. Change the object reference in the URL to `/profile/2`.
4. The server returns `analyst2`'s profile with no ownership check.
5. Read the note field to recover the HORIZ-02 flag.

## Flag
CITS3006{HORIZ02_IDOR_OBJECT}
