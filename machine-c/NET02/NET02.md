# NET-02 — Anonymous Rsync Information Disclosure

## Category
Network vulnerability

## Objective
Discover an exposed rsync service and retrieve sensitive files without authentication.

## Initial Access
Network access to the vulnerable Ubuntu machine.

## Vulnerability
An rsync daemon was exposed on TCP port 1873 with an anonymously accessible module named legacy-sync. The module permits unauthenticated read access to files intended for internal synchronisation.

## Exploitation
1. Scan the target and identify TCP port 1873.
2. Identify the service as rsync.
3. Enumerate the available rsync modules.
4. Discover the legacy-sync module.
5. List the files exposed by the module.
6. Download network-backup.txt without authentication.
7. Recover the NET-02 flag from the exposed backup.

## Chain position
The pre-audit config dump inside `network-backup.txt` also leaks the `analyst1`
credentials for the Halcyon Systems Analyst Console (HORIZ-02). This stage is
reached from the WEB-02 reviewer console, whose internal ops note discloses that
the rsync service on tcp/1873 is still exposed.

`WEB-02 (XSS) → NET-02 (this) → HORIZ-02 (IDOR)`

## Flag
CITS3006{NET02_ANON_RSYNC}

## Evidence
- Nmap service discovery.
- Rsync module enumeration.
- Exposed file listing.
- Anonymous file download.
- Flag recovery.

## Result
Successful exploitation of an anonymously accessible rsync service and recovery of the NET-02 flag.
