#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
DATA="$PREFIX/var/lib/postgresql"
LOG="$DATA/logfile"
PORT=5432

echo "Stopping stray postgres --check processes..."
pkill -f -15 "postgres .*--check" || true
sleep 2
if ps aux | grep -E "postgres|postgresql" | grep -v grep > /dev/null; then
  echo "Force-killing remaining postgres processes..."
  pkill -f -9 "postgres .*--check" || true
  sleep 1
fi
ps aux | grep -E "postgres|postgresql" | grep -v grep || echo "no postgres process"

echo "Resetting data directory..."
rm -rf "$DATA"
mkdir -p "$DATA"
chmod 700 "$DATA"

echo "Initializing database cluster..."
initdb -D "$DATA" --no-locale --encoding=UTF8

echo "Starting Postgres (log -> $LOG)..."
pg_ctl -D "$DATA" -l "$LOG" start -o "-p $PORT" || { echo "pg_ctl start failed; showing logfile tail:"; tail -n 200 "$LOG"; exit 1; }

echo "Waiting for Postgres to accept connections..."
for i in {1..20}; do
  if psql -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
    echo "Postgres is up."
    break
  fi
  echo "waiting... ($i)"
  sleep 1
  if [ $i -eq 20 ]; then
    echo "Postgres did not come up; last 200 lines of logfile:"
    tail -n 200 "$LOG"
    exit 1
  fi
done

TENANT_USER="tenantuser"
TENANT_PASS="tenantpass"
TENANT_DB="tenantdb"

echo "Creating tenant user and db..."
psql -d postgres -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='${TENANT_USER}') THEN CREATE USER ${TENANT_USER} WITH PASSWORD '${TENANT_PASS}'; END IF; END\$\$;"
psql -d postgres -c "CREATE DATABASE ${TENANT_DB} OWNER ${TENANT_USER};" || echo "Database may already exist."

echo "All done. Log tail:"
tail -n 50 "$LOG"
