# CITS3006 CTF Project — Team Plan (Task 1)

AS of week 5

## Team structure (5 people)

**3 Machine Builders** — each owns one fully self-contained machine/chain: 

- Machine A — Builder: _TBD_
- Machine B — Builder: _TBD_
- Machine C — Builder: _TBD_

Each machine independently contains:
- 1 web vulnerability (distinct type per machine — e.g. SQLi on A, XSS on B, IDOR/CSRF on C — must be genuinely different types, not the same bug reused)
- 1 network-based vulnerability (distinct type per machine)
- 1 horizontal privilege escalation path
- 1 vertical privilege escalation path
- 1 reverse-engineering vulnerability

This hits the required minimums exactly: 3 web, 3 network, 3 horizontal PE, 3 vertical PE, 3 RE.

**2 Advanced Builders** — own the advanced challenges, now embedded per machine (see below):
- AES-CTR nonce reuse — Builder: Vraj — embedded in **Machine A** (`machine-a/ADV_aes-ctr`)
- AES-CTR nonce reuse (Vatsal's build) — embedded in **Machine B** (`machine-b/ADV_aes-ctr`)
- AI prompt injection — Builder: Maharshi — embedded in **Machine C** (`machine-c/ADV_prompt-injection`)

**Design change (team decision):** the advanced challenges are no longer two separate
Restricted-VLAN hosts reached by fan-in. Each is embedded directly inside a machine as
an extra challenge folder. Machines A and B carry AES-CTR (distinct flags); Machine C
carries the AI prompt injection. Two distinct advanced *types* are still present. Note
the AES-CTR type is reused across A and B — confirm that's acceptable against the rubric.

## Network topology

One shared, themed environment (e.g. a fictional company network) containing Machines A/B/C, rather than unrelated separate sites. This gives a coherent theme (rewarded for D/HD) and a single setup package for Task 2.

**Design rule — each machine is fully self-contained.** Every machine (A, B, C) is
rootable on its own and now also carries its own embedded advanced challenge, so there
is no separate advanced tier and no cross-machine credential dependency.

There is no Restricted VLAN and no fan-in wiring anymore — the advanced challenges live
inside the machines that host them.

## Build sequence

1. Each Machine Builder builds their machine fully self-contained and independently rootable.
2. Advanced Builders build their advanced vuln, which is dropped into a machine's `ADV_*` folder.
3. Cross-test: every member also tests at least one other member's machine — multiple testers per machine is fine, no single-owner bottleneck on QA.
4. Compile the report (exploit map covering all root paths, sample solutions, setup instructions) — sooner rather than at the deadline, since undocumented/unreproducible challenges score zero on difficulty regardless of how good the underlying vuln is.

## Open items

- Assign names to the 5 role labels above, and also mention which vlun you are planning to use when youve researched it. ( FCFS ig)
- Advanced challenges chosen: AES-CTR (crypto) on A and B, AI prompt injection on C.
- Nail down the shared network's theme/narrative and IP scheme.
- Individual contribution logging: given the workload isn't perfectly even (machine builders build 5 vulns each vs. 1 for advanced builders, offset by advanced builders taking on cross-testing/integration), SO HELP OTHER WHEN DONE AND ASK FOR HELP WHEN NEEDED 
