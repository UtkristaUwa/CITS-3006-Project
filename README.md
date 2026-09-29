# CITS-3006-Project
A CTF project consisting of three machines. Each machine has five core vulnerabilities plus one embedded advanced vulnerability (Machine A: AES-CTR nonce reuse; Machines B and C: AI prompt injection).

## Team members

| NAME                     | StudentID   |   GitHubID         |
|--------------------------|-------------|--------------------|
| Utkrista Sen             | 24145884    | UtkristaUwa        |
|  Vatsal Padsala          | 24323822    | vatsalpadsala28082 |
| Het Patel                | 24498631    |  Het-eng           |
| Maharshi Patel           | 24747899    | Maharshi1-coder    |
## Machines and Vulns
 
| Machine | Owner | Web | Network | Horizontal PE | Vertical PE | RE |
|---|---|---|---|---|---|---|
| **A** | Utkrista | IDOR | ARP spoofing MITM | Group misconfig | Leaked backup (passphrase gated by the AES-CTR advanced challenge) | XOR encoded |
| **B** | Vatsal  | Server-side template injection | Unauthenticated Redis exposure|  JWT forgery | SUID shared-library hijacking |Transformed validation  |
| **C** | Het | XSS | Anonymous Rsync information disclosure | Idor | Path Hijacking via privileged Maintenance Script | Obfuscated Secret Recovery |

 
## Advanced Vulns (embedded per machine)

The two advanced challenges are no longer separate hosts on a Restricted VLAN.
Each is now embedded inside a machine as an extra challenge folder:

| Machine | Advanced vuln | Category | Built by | Folder |
|---|---|---|---|---|
| **A** | AES-CTR nonce reuse | Cryptographic (known-plaintext keystream recovery) | Vraj | `machine-a/ADV_aes-ctr` |
| **B** | AI prompt injection | AI-related (instruction override / context leak) | Maharshi | `machine-b/ADV_prompt-injection` |
| **C** | AI prompt injection | AI-related (instruction override / context leak) | Maharshi | `machine-c/ADV_prompt-injection` |

**How each is wired in:**
- **Machine A (AES-CTR)** is a *required link in the root path*, not a side-quest. The
  sysadmin SSH-key passphrase is no longer stored in the clear — it is protected by the
  reused-nonce ciphertext dropped into the pre-audit backup. Solving the AES-CTR nonce
  reuse recovers the passphrase (and the advanced flag), which is what enables vertical
  PE → root. No crypto solve, no vertical PE.
- **Machine B (AI prompt injection)** runs as a Dockerised assistant on port 8085.
- **Machine C (AI prompt injection)** runs on port 8086 with a distinct flag, so B and C
  are independently solvable despite sharing the technique.


## link to project 


https://uwacyber.gitbook.io/cits3006/cits3006-assessments/project


## Grading 

25% Creating CTF Challenges (T1) 
10% Solving Live (T2-1) 
15% Solving All Challenges (T2-2) 
25% Live Demo (T3) 
25% Individual Contributions (T1–T3).

