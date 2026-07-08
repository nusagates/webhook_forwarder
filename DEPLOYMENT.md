# Ubuntu Production Deployment Guide

Deploying the Webhook Forwarder on an Ubuntu server involves running the FastAPI backend via `systemd` (using `uvicorn`) and using `Nginx` as a web server to serve the static frontend files and act as a reverse proxy for the API.

Since the React frontend compiles into static HTML/JS/CSS files, **you do NOT need to install Node.js on your production server**. You can build it locally on your computer and simply upload the built files.

## 1. Local Machine: Build the Frontend
Before touching the server, open a terminal on your **Local Computer** and build the React app:

```bash
cd frontend
npm run build
```
This will generate a `dist/` folder inside the `frontend/` directory containing all your static production files. 

*Note: Since `dist/` is usually ignored by Git, you will need to upload this folder directly to your server later (e.g., using `scp`, `rsync`, or FileZilla).*

## 2. Server: Install Prerequisites
SSH into your Ubuntu server and install the required backend packages (Python, Nginx, and uv):

```bash
sudo apt update
sudo apt install -y nginx curl

# Install uv (Lightning-fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

## 3. Server: Setup the Application
Clone your repository into the `/var/www/` directory.

```bash
sudo mkdir -p /var/www/webhook_forwarder
sudo chown -R $USER:$USER /var/www/webhook_forwarder

# Clone your project
git clone https://github.com/nusagates/webhook_forwarder.git /var/www/webhook_forwarder
cd /var/www/webhook_forwarder
```

## 4. Server: Configure the Backend (FastAPI)
Set up the Python virtual environment and install dependencies using `uv`.

```bash
cd /var/www/webhook_forwarder
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Create a Systemd Service for the Backend
We will use `systemd` to keep the backend running in the background and restart it automatically if it crashes.

```bash
sudo nano /etc/systemd/system/webhook-backend.service
```
Paste the following configuration:
```ini
[Unit]
Description=Webhook Forwarder Backend (FastAPI)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/webhook_forwarder
Environment="PATH=/var/www/webhook_forwarder/.venv/bin"
ExecStart=/var/www/webhook_forwarder/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8006
Restart=always

[Install]
WantedBy=multi-user.target
```
Start and enable the backend service:
```bash
sudo chown -R www-data:www-data /var/www/webhook_forwarder
sudo systemctl daemon-reload
sudo systemctl start webhook-backend
sudo systemctl enable webhook-backend
```

## 5. Server: Configure Nginx
Nginx will serve the compiled React static files and forward API/WebSocket requests to your Python backend.

```bash
sudo nano /etc/nginx/sites-available/webhook_forwarder
```
Paste the following configuration (replace `your_domain.com` with your actual domain or IP address):

```nginx
server {
    listen 80;
    server_name your_domain.com; # Or your server's IP address

    # Serve the compiled React Frontend from the uploaded dist/ folder
    root /var/www/webhook_forwarder/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy /api requests to FastAPI Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8006;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy WebSocket connections for Live Logs
    location /ws/ {
        proxy_pass http://127.0.0.1:8006;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

Enable the Nginx configuration and restart the service:
```bash
sudo ln -s /etc/nginx/sites-available/webhook_forwarder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 6. Expose to Internet via Cloudflare Tunnel (Recommended)
Since you are likely running this behind a router/NAT, the easiest and most secure way to expose the application without dealing with Port Forwarding or SSL certificates is by using Cloudflare Tunnels (Zero Trust).

```bash
# 1. Install Cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# 2. Authenticate and Install the Tunnel Service
# Replace YOUR_TUNNEL_TOKEN with the token from your Cloudflare Zero Trust dashboard
sudo cloudflared service install YOUR_TUNNEL_TOKEN

# 3. Start the service
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### Configure Cloudflare Zero Trust
In your Cloudflare Zero Trust Dashboard, go to your Tunnel's **Public Hostname** settings and route your domain as follows:
- **Domain:** `hook.web.id`
- **Service:** `HTTP`
- **URL:** `127.0.0.1:80`

Cloudflare will automatically provide a secure HTTPS connection for your visitors and route the traffic safely to your local Nginx server!

## 7. Access Your Application
Open your browser and navigate to `https://your_domain.com`. Your Webhook Forwarder is now live in production!
