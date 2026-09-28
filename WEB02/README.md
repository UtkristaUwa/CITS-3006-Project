# WEB-02 — Reflected XSS

## Category
Web vulnerability

## Objective
Exploit a reflected cross-site scripting vulnerability in the support-search function.

## Vulnerability
The search parameter is inserted directly into the HTML response without output encoding.

## Flag
CITS3006{WEB02_REFLECTED_XSS}

## Intended Technique
Use a JavaScript payload through the reflected search parameter to execute script in the portal's origin.
