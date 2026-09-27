#!/bin/bash
# VERT-03 deploy helper (run as root on the target).
# Installs the SUID binary + a writable lib dir (the vulnerability),
# then plants the root-only flag with a breadcrumb pointing to RE-03.
install -d -m 0755 /opt/vert03
install -d -m 0777 /opt/vert03/lib
cp ctf-vert03 /usr/local/bin/ctf-vert03
cp lib/libctfhelper.so /opt/vert03/lib/libctfhelper.so
chown root:root /usr/local/bin/ctf-vert03
chmod u+s /usr/local/bin/ctf-vert03
echo 'CITS3006{VERT03_SUID_LIBRARY_HIJACK} -- Next: reverse the root-only binary at /root/re03' > /root/vert03_flag.txt
chmod 600 /root/vert03_flag.txt
echo "VERT-03 deployed. Flag planted with breadcrumb to RE-03."
