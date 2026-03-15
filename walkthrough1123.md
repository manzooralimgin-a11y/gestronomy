# Deployment Walkthrough: DAS El Magdeburg

This guide details the process of taking the system live on a production host.

## 1. Preflight: Prepare the Target Host
Run these commands on your VPS (Ubuntu 22.04+ recommended) before deploying.

### Install Prerequisites
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw jq
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install -y docker-compose-plugin
```

### Setup Deploy User & Firewall
```bash
sudo adduser deploy
sudo usermod -aG docker deploy
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 2. Domain & DNS Setup
Configure your DNS provider with the following A records pointing to your host IP:
- `api.your-domain.com`
- `dashboard.your-domain.com`
- `admin.your-domain.com`
- `auth.your-domain.com`

## 3. Deployment Steps

### Step 1: Initialize the Environment
Clone the repository and run the deployment script:
```bash
git clone <your-repo-url> app && cd app
chmod +x ./deploy.sh
./deploy.sh
```

### Step 2: Configure Production Secrets
Edit `production.env` to set your domains, email, and API keys:
```bash
# Gateway & Domains
API_DOMAIN=api.your-domain.com
DASHBOARD_DOMAIN=dashboard.your-domain.com
ADMIN_DOMAIN=admin.your-domain.com
AUTH_DOMAIN=auth.your-domain.com
ACME_EMAIL=your-email@example.com

# Third-party Keys
STRIPE_SECRET_KEY=sk_prod_...
ANTHROPIC_API_KEY=xkeys-at-...
```

### Step 3: Apply Changes
```bash
docker compose -f docker-compose.prod.yml up -d
```

## 4. Post-Deploy Verification
1. **Health Check**: Run `./scripts/health-check.sh`
2. **Container Status**: `docker compose -f docker-compose.prod.yml ps`
3. **Logs**: `docker compose -f docker-compose.prod.yml logs -f traefik` (to check SSL issuance)

## 5. Hardening & Scaling
- **Backups**: Implement daily PostgreSQL backups using `pg_dump`.
- **Monitoring**: Traefik provides a dashboard on port 8080 (if enabled) or use Prometheus/Grafana.
- **Scaling**: Scale the `nexus` or `inventory` services using `docker compose up -d --scale nexus=3`.
