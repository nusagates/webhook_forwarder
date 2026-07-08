# Ubuntu Production Deployment Guide

Deploying the Webhook Forwarder on an Ubuntu server involves running the FastAPI backend via `systemd` (using `uvicorn`), building the React frontend into static files, and using `Nginx` as a web server and reverse proxy.

## 1. Install Prerequisites
SSH into your Ubuntu server and install the required packages:

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx curl

# Install Node.js (Version 18.x)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

## 2. Setup the Application
Clone your repository into the `/var/www/` directory.

```bash
sudo mkdir -p /var/www/webhook_forwarder
sudo chown -R $USER:$USER /var/www/webhook_forwarder

# Clone your project (replace with your actual git URL)
git clone https://github.com/your-username/webhook-forwarder.git /var/www/webhook_forwarder
cd /var/www/webhook_forwarder
```

## 3. Configure the Backend (FastAPI)
Set up the Python virtual environment and install dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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
ExecStart=/var/www/webhook_forwarder/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
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

## 4. Build the Frontend (React)
Now, compile the React application into static HTML/JS/CSS files.

```bash
cd /var/www/webhook_forwarder/frontend
npm install
npm run build
```
*(This will generate a `dist/` folder containing your compiled frontend).*

## 5. Configure Nginx
Nginx will serve the React static files and forward API/WebSocket requests to your Python backend.

```bash
sudo nano /etc/nginx/sites-available/webhook_forwarder
```
Paste the following configuration (replace `your_domain.com` with your actual domain or IP address):

```nginx
server {
    listen 80;
    server_name your_domain.com; # Or your server's IP address

    # Serve the React Frontend
    root /var/www/webhook_forwarder/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy /api requests to FastAPI Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy WebSocket connections for Live Logs
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
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

## 6. Access Your Application
That's it! Open your browser and navigate to `http://your_domain.com` (or your server's public IP). Your Webhook Forwarder is now live in production!
