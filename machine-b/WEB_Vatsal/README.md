# WEB-03 — Server-Side Template Injection

## Category
Web vulnerability

## Objective
Exploit an SSTI vulnerability in the report-generation function.

## Vulnerability
User-controlled input is inserted directly into a Jinja template and evaluated server-side.

## Flag
CITS3006{WEB03_SSTI_TEMPLATE_INJECTION}

## Intended Technique
Identify template expression evaluation, enumerate the template execution context, and use server-side template capabilities to access the protected training artifact.
