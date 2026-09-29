#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/* CITS3006 VERT-02 — SUID PATH Hijacking
 *
 * Installed SUID-root (chmod 4755, owner root). It runs a maintenance
 * copy step, but invokes `cp` by NAME rather than by absolute path, so
 * the command is resolved through $PATH. setuid(0)/setgid(0) make the
 * real IDs root too, so the spawned shell does not drop privileges —
 * whatever `cp` resolves to therefore runs as root.
 */
int main(void) {
    setuid(0);
    setgid(0);
    printf("Running CTF maintenance...\n");
    /* VULNERABLE: relative command name, PATH-resolved */
    system("cp /var/lib/ctf-maintenance/report.txt /tmp/ctf-report.txt");
    printf("Maintenance completed.\n");
    return 0;
}
