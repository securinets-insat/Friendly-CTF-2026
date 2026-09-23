# Deploying the mobile backend

One container serves every mobile challenge that talks to a server.

| Port | Service | Used by |
|------|---------|---------|
| 8000 | `app.py --http` | plain-HTTP challenges (login, IDOR, JWT, activation, `/verify`, `/debrief`) |
| 8443 | `app.py --https` | certificate-pinning challenge |
| 9090 | `rogue_sdk_collector.py` | the rogue SDK challenge (#14) |

## 1. Put the flags file in place

`flags.json` is gitignored and must never be committed. Copy it beside
`docker-compose.yml` on the server:

```bash
scp flags.json <user>@<VPS_IP>:~/ctf/mobile/deploy/flags.json
```

It is bind-mounted read-only into the container. The service refuses to start
without it.

## 2. Open the ports

TCP 8000, 8443 and 9090 inbound. Azure CLI:

```bash
az vm open-port -g <RESOURCE_GROUP> -n <VM_NAME> --port 8000,8443,9090 --priority 1020
```

## 3. Start

```bash
cd mobile/deploy
docker compose up -d --build
docker compose ps
```

## 4. Check it before anyone plays

```bash
curl http://<VPS_IP>:8000/health
curl -k https://<VPS_IP>:8443/health
curl -X POST http://<VPS_IP>:9090/collect -H "Content-Type: application/json" \
  -d '{"device_id":"x","install_id":"y","event":"app_session_start"}'
```

All three must answer. A dead collector on 9090 fails silently: nothing in the
app breaks, but the #14 flag is gone.

## 5. The hostname has to match the APK

The APK talks to a fixed hostname, and the TLS cert in `certs/` is issued for
`ctf.securinets.tn`. Point that DNS name at the VPS. If the hostname changes,
the cert, the pin in `certs/okhttp_pin.txt` and the app's `CERT_PIN` all have
to change together, or the pinning challenge breaks.

## Useful commands

```bash
docker compose logs -f mobile-backend
docker compose restart mobile-backend
docker compose down
```
