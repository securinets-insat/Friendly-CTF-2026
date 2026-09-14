#!/bin/sh
set -e

if [ -z "$FLASK_SECRET" ]; then
    export FLASK_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi


exec gunicorn \
    --bind 0.0.0.0:5002 \
    --control-socket /tmp/gunicorn.ctl \
    app:app