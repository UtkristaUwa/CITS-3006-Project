# CITS-3006-Project
A CTF project consisting of three machines. Each machine has five core vulnerabilities plus one embedded advanced vulnerability (Machines A and B: AES-CTR nonce reuse; Machine C: AI prompt injection).


## Group name
- Lets_do_it

## Team members

| NAME                     | StudentID   |   GitHubID         |
|--------------------------|-------------|--------------------|
| Utkrista Sen             | 24145884    | UtkristaUwa        |
|  Vatsal Padsala          | 24323822    | vatsalpadsala28082 |
| Het Patel                | 24498631    |  Het-eng           |
| Maharshi Patel           | 24747899    | Maharshi1-coder    |
| Vraj  Hirpara            | 24561231    | Vrajhirpara        |
## Machines and Vulns
 
| Machine | Owner | Web | Network | Horizontal PE | Vertical PE | RE |
|---|---|---|---|---|---|---|
| **A** | Utkrista | IDOR | ARP spoofing MITM | Group misconfig | Leaked backup (passphrase gated by the AES-CTR advanced challenge) | XOR encoded |
| **B** | Vatsal  | Server-side template injection | Unauthenticated Redis exposure|  JWT forgery | SUID shared-library hijacking |Transformed validation  |
| **C** | Het | XSS | Anonymous Rsync information disclosure | Idor | Path Hijacking via privileged Maintenance Script | Obfuscated Secret Recovery |

 
## Advanced Vulns (embedded per machine)

| Machine | Advanced vuln | Category | Built by | Folder |
|---|---|---|---|---|
| **A** | AES-CTR nonce reuse | Cryptographic (known-plaintext keystream recovery) | Vraj | `machine-a/ADV_aes-ctr` |
| **B** | AES-CTR nonce reuse | Cryptographic (known-plaintext keystream recovery) | Vraj | `machine-b/ADV_aes-ctr` |
| **C** | AI prompt injection | AI-related (instruction override / context leak) | Maharshi | `machine-c/ADV_prompt-injection` |


## Repository layout

.
├── machine-a/ # Meridian Robotics dev portal (self-contained)
│ └── ADV_aes-ctr/ # embedded advanced crypto challenge
├── machine-b/ # Evergreen Analytics (self-contained)
│ └── ADV_aes-ctr/ # embedded advanced crypto challenge
├── machine-c/ # self-contained
│ └── ADV_prompt-injection/
└── README.md
