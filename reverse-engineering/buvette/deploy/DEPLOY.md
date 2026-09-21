# Deploying the remote challenges on an Azure VPS

| Challenge      | Folder                             | Port  | Player command         |
|----------------|------------------------------------|-------|------------------------|
| Bankai         | `Crypto/Wave3 - BLEACH/Bankai`     | 31337 | `nc <VPS_IP> 31337`    |
| Gestuga Tencho | `Crypto/Wave3 - BLEACH/bruteforce` | 1337  | `nc <VPS_IP> 1337`     |
| Buvette INSAT  | `Rev/buvette`                      | 1338  | `nc <VPS_IP> 1338`     |

## 1. Create the VM
Azure Portal -> Virtual machines -> Create. Ubuntu Server 24.04 LTS, size B2s (2 vCPU / 4 GB) is plenty.
Authentication: SSH public key.

## 2. Open the ports (Network Security Group)
VM -> Networking -> Add inbound port rule, for each of `1337`, `1338`, `31337`:
Source `Any`, Protocol `TCP`, Action `Allow`.

Or with Azure CLI:
```bash
az vm open-port -g <RESOURCE_GROUP> -n <VM_NAME> --port 1337,1338,31337 --priority 1010
```

## 3. Install Docker on the VM
```bash
ssh azureuser@<VPS_IP>
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER && newgrp docker
```

## 4. Upload and start
From your PC (Git Bash / PowerShell), in the `Securinets Friendly CTF` folder:
```bash
scp -r docker-compose.yml Crypto Rev azureuser@<VPS_IP>:~/ctf/
```
On the VM:
```bash
cd ~/ctf
docker compose up -d --build
docker compose ps
```

## 5. Test
```bash
nc <VPS_IP> 31337
nc <VPS_IP> 1337
nc <VPS_IP> 1338
```

## 6. Update CTFd
Replace `<VPS_IP>` in `connection_info` of the three `challenge.yml` files, then sync with ctfcli
(`ctf challenge install` / `ctf challenge sync`).

## Useful commands
```bash
docker compose logs -f bankai       # watch connections
docker compose restart buvette      # restart one challenge
docker compose down                 # stop everything
```
