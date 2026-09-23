# NET-03 — Unauthenticated Redis Exposure

## Category
Network vulnerability

## Objective
Discover the exposed Redis service and retrieve sensitive data without authentication.

## Service
Redis listens on TCP port 6380.

## Intended Technique
1. Discover TCP port 6380.
2. Identify the service as Redis.
3. Connect without authentication.
4. Enumerate Redis keys.
5. Retrieve the sensitive training value.
6. Recover the NET-03 flag.

## Included Files
- cits3006-net03.service
- redis-net03.conf

See the project documentation for the complete exploitation procedure.
