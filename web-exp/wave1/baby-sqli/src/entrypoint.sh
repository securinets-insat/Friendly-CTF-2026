#!/bin/sh
set -e

if [ -z "$FLASK_SECRET" ]; then
    export FLASK_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

if [ -z "$ADMIN_PASSWD" ]; then
    export ADMIN_PASSWD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
fi

exec gunicorn \
    --bind 0.0.0.0:5000 \
    --control-socket /tmp/gunicorn.ctl \
    app:app