# CITS3006 CTF Project — Team Plan (Task 1)

AS of week 5

## Team structure (5 people)

**3 Machine Builders** — each owns one fully self-contained machine/chain: 

- Machine A — Builder: Utkrista
- Machine B — Builder: _TBD_
- Machine C — Builder: _TBD_

Each machine independently contains:
- 1 web vulnerability (distinct type per machine — e.g. SQLi on A, XSS on B, IDOR/CSRF on C — must be genuinely different types, not the same bug reused)
- 1 network-based vulnerability (distinct type per machine)
- 1 horizontal privilege escalation path
- 1 vertical privilege escalation path
- 1 reverse-engineering vulnerability

This hits the required minimums exactly: 3 web, 3 network, 3 horizontal PE, 3 vertical PE, 3 RE.

**2 Advanced Builders** — each owns one of the two required advanced challenges: ( must be different )
- Advanced Service #1  — Builder: _TBD_
- Advanced Service #2  — Builder: _TBD_

Rubric requires exactly 2 advanced challenges total, not one per machine.

## Network topology

One shared, themed environment (e.g. a fictional company network) containing Machines A/B/C and the two Advanced Services, rather than unrelated separate sites. This gives a coherent theme (rewarded for D/HD) and a single setup package for Task 2. 

**Design rule — no circular credential loops.** Each machine (A, B, C) must be fully rootable on its own, with zero dependency on the advanced services. That's the safety net: if the shared-service wiring breaks or runs out of time, all 3 machines still stand alone as complete, gradeable root paths.

On top of that baseline, the advanced services are **fan-in points, not loop points**:
- Advanced Service #1 is reachable via credentials obtained from rooting Machine A *or* Machine C (two alternate entry routes into the same flag, just an example of machine A and C can be changed later).
- Advanced Service #2 is reachable via credentials obtained from rooting Machine B *or* Machine C . 
- Nothing flows back out of the advanced services into A/B/C. 

This still earns credit for "distinct root paths, some combining multiple vulnerabilities" (multiple valid routes into the same advanced-service flag) without the complexity or illogic of a full loop.

## Build sequence

1. Each Machine Builder builds their machine fully self-contained and independently rootable first — no dependency on advanced services.
2. Advanced Builders build their advanced vuln in parallel, working against a mocked/assumed credential rather than waiting on a finished machine.
3. Once both sides are solid, wire in the fan-in links (A/C → Adv1, B/C → Adv2).
4. Cross-test: every member also tests at least one other member's machine — multiple testers per machine is fine, no single-owner bottleneck on QA.
5. Compile the report (exploit map covering all root paths, sample solutions, setup instructions) — sooner rather than at the deadline, since undocumented/unreproducible challenges score zero on difficulty regardless of how good the underlying vuln is.

## Open items

- Assign names to the 5 role labels above, and also mention which vlun you are planning to use when youve researched it. ( FCFS ig)
- Decide which two of Kernel / Windows / AI-related the two Advanced Builders are actually building.
- Nail down the shared network's theme/narrative and IP scheme before wiring the fan-in links.
- Individual contribution logging: given the workload isn't perfectly even (machine builders build 5 vulns each vs. 1 for advanced builders, offset by advanced builders taking on cross-testing/integration), SO HELP OTHER WHEN DONE AND ASK FOR HELP WHEN NEEDED 
