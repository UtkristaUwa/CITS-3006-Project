#!/bin/bash
# Loads NET-03 flag + a breadcrumb pointing to WEB-03 into Redis.
HOST="${1:-127.0.0.1}"
PORT=6380
redis-cli -h "$HOST" -p "$PORT" SET cits3006:net03:backup "CITS3006{NET03_REDIS_UNAUTH}"
redis-cli -h "$HOST" -p "$PORT" SET cits3006:net03:note "Recon note: internal report generator is live on port 8084 (its name field looks unsafe)."
echo "NET-03 data loaded on $HOST:$PORT"
