# Webhook Forwarder

Webhook Forwarder is a full-stack web application (built with FastAPI and React) designed to receive, log, and forward incoming webhooks from third-party services (such as Meta, Stripe, GitHub, etc.) to one or multiple destination servers simultaneously.

This application is highly useful as a middleware to monitor webhook traffic in real-time before the data touches your main production servers.

## 🌟 Use Cases

This application can be utilized for various real-world scenarios:

1. **Webhook Fan-Out (One-to-Many):** 
   You receive a single webhook from a Payment Gateway (e.g., Stripe) but want to forward that payment notification to 3 different places simultaneously: your API Database Server, Accounting System, and a Telegram Bot. Webhook Forwarder splits and delivers the webhook to multiple destinations concurrently.
   
2. **Local Development & Debugging:** 
   Instead of constantly checking production server logs when testing a Meta WhatsApp webhook, you can point the webhook to this application to inspect the JSON payload sent by Meta in real-time (Live Logs), without writing any code on your main server first.

3. **First-Layer Security & Authentication:**
   This application supports *HMAC Signatures*, *Bearer Tokens*, and *Meta Challenge Handshakes*. You can protect your main servers from spam by letting Webhook Forwarder reject illegal requests (401/403) before they even reach your internal network.

## 🚀 Key Features

- **Multi-Tenant System (SaaS-like):** Supports user registration, login, and project isolation.
- **Dynamic Authentication:** Supports Open endpoints, Basic Auth, Bearer Tokens, HMAC Signatures, and Meta Handshakes out of the box.
- **Live Logs (WebSockets):** Real-time monitoring of incoming webhooks directly on the web interface.
- **Multi-Destination Forwarding:** Forward incoming webhooks to an unlimited number of destination URLs simultaneously.
- **Background Processing:** Forwarding is handled in background tasks, ensuring the webhook sender (e.g., Meta) receives an immediate < 50ms response to prevent timeouts.

## 🛠️ Prerequisites

Make sure your machine/server has the following installed:
- **Python 3.10+** (along with `uv` or `pip` package manager)
- **Node.js 18+** (along with `npm`)
- Windows (recommended for quickstart script) or Linux/macOS.

## 💻 Installation

**1. Clone the Repository & Backend Setup (Python/FastAPI)**
```bash
# Clone the repository
git clone https://github.com/nusagates/webhook_forwarder.git

# Navigate into the project folder
cd webhook_forwarder

# Create a virtual environment and install dependencies using uv (recommended)
uv venv
uv pip install -r requirements.txt
```

**2. Frontend Setup (React/Vite)**
```bash
# Open a new terminal and navigate to the frontend folder
cd frontend

# Install React dependencies
npm install
```

## 🏃‍♂️ Running the Application

**For Windows Users (Easiest Method):**
Simply double-click (or run in the terminal) the following script:
```bash
.\start_server.bat
```
This script will automatically open 2 new terminals to run both the Backend and Frontend simultaneously. Once initialized, your browser will automatically open `http://localhost:5173`.

**Manual Method (If not using .bat):**
1. **Terminal 1 (Backend):**
   ```bash
   uv run uvicorn main:app --port 8000
   ```
2. **Terminal 2 (Frontend):**
   ```bash
   cd frontend
   npm run dev
   ```

## 📖 Quick Usage Guide

1. **Register & Login:** Open `http://localhost:5173`. Create a new account on the Register page, then Login.
2. **Create a Project:** Once logged in, create your first Project (e.g., "WhatsApp Integration").
3. **Create an Endpoint:** Click the **Endpoints** menu on the left sidebar, then click **New Endpoint**.
   - Provide a name (e.g., "WhatsApp Webhook") and a slug (e.g., `wa-incoming`).
   - Select the Authentication Type (e.g., Meta Challenge Handshake).
   - Save the settings. You will receive a **Unique Webhook URL**.
4. **Add Destinations:** On the newly created Endpoint card, click **Add Destination**. Enter the URL of your main server that is responsible for processing the webhook logic.
5. **Monitor Traffic:** Open the **Live Logs** menu. Every time a webhook hits your unique URL, the JSON log will appear on the screen in real-time, and the system will instantly forward it to your specified Destinations.

---
*Developed with FastAPI, React, and Material UI.*
