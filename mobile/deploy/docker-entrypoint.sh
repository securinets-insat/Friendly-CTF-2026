#!/usr/bin/env sh
# Container entrypoint. Same three services as start_all.sh, minus the log
# files that script writes to disk -- those need a writable ./logs, which the
# container filesystem deliberately does not have (read_only: true). Docker
# already captures stdout/stderr per container, so all three processes log
# there instead.
set -eu

term() {
    kill -TERM "$app_http" "$app_https" "$collector" 2>/dev/null || true
}
trap term TERM INT

python3 app.py --http --port 8000 &
app_http=$!

python3 app.py --https --port 8443 &
app_https=$!

python3 rogue_sdk_collector.py --port 9090 &
collector=$!

wait "$app_http" "$app_https" "$collector"
