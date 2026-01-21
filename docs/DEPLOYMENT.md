# Sakti-Link Edge Server Deployment Guide

## Table of Contents
1. [Hardware Requirements](#hardware-requirements)
2. [Software Prerequisites](#software-prerequisites)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Running the Server](#running-the-server)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Hardware Requirements

### Minimum Requirements (Small Community - 50 users)
- **Device**: Raspberry Pi 4 (4GB RAM) or equivalent
- **Storage**: 32GB microSD card
- **Network**: WiFi or Ethernet connection (optional for offline mode)
- **Power**: 5V/3A power supply with backup

### Recommended Requirements (Medium Community - 200 users)
- **Device**: Raspberry Pi 4 (8GB RAM) or Intel NUC
- **Storage**: 64GB microSD or SSD
- **Network**: Ethernet preferred
- **Power**: UPS backup recommended

### Optimal Requirements (Large Community - 500+ users)
- **Device**: Small server or high-end mini PC
- **CPU**: 4+ cores
- **RAM**: 16GB+
- **Storage**: 256GB+ SSD
- **Network**: Gigabit Ethernet
- **Power**: UPS backup required

---

## Software Prerequisites

### Operating System
- **Recommended**: Ubuntu 22.04 LTS or Raspberry Pi OS (64-bit)
- **Also supported**: Debian 11+, Ubuntu 20.04+

### Required Software

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.9+
sudo apt-get install python3.10 python3-pip python3-venv -y

# Install Redis
sudo apt-get install redis-server -y

# Install SQLCipher (for encrypted database)
sudo apt-get install sqlcipher libsqlcipher-dev -y

# Install audio processing libraries
sudo apt-get install ffmpeg libsndfile1 -y

# Install build tools
sudo apt-get install build-essential git -y
```

---

## Installation Methods

### Method 1: Docker Installation (Recommended)

#### Step 1: Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### Step 2: Clone Repository
```bash
git clone https://github.com/your-org/sakti-link-backend.git
cd sakti-link-backend
```

#### Step 3: Configure Environment
```bash
cp .env.example .env
nano .env  # Edit configuration
```

#### Step 4: Build and Run
```bash
docker-compose up -d
```

#### Step 5: Initialize Database
```bash
docker exec -it sakti-link-edge python scripts/init_db.py
```

#### Step 6: Check Status
```bash
docker-compose ps
curl http://localhost:8000/health
```

---

### Method 2: Manual Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/sakti-link-backend.git
cd sakti-link-backend
```

#### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment
```bash
cp .env.example .env
nano .env  # Edit configuration
```

#### Step 5: Create Directories
```bash
mkdir -p data models logs cache
```

#### Step 6: Download AI Models
```bash
python scripts/download_models.py
```

#### Step 7: Initialize Database
```bash
python scripts/init_db.py
```

#### Step 8: Start Redis
```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### Step 9: Run Server
```bash
cd edge_server
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

### Method 3: Systemd Service (Production)

#### Step 1: Complete Manual Installation (Steps 1-7 above)

#### Step 2: Create Service File
```bash
sudo nano /etc/systemd/system/sakti-link.service
```

Add content:
```ini
[Unit]
Description=Sakti-Link Edge Server
After=network.target redis.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/sakti-link-backend/edge_server
Environment="PATH=/home/pi/sakti-link-backend/venv/bin"
ExecStart=/home/pi/sakti-link-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Step 3: Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable sakti-link
sudo systemctl start sakti-link
```

#### Step 4: Check Status
```bash
sudo systemctl status sakti-link
```

---

## Configuration

### Essential Settings

Edit `.env` file:

```bash
# Security (IMPORTANT: Change these!)
DATABASE_KEY=generate-strong-32-char-key-here
SECRET_KEY=generate-strong-secret-key-here

# Language Settings
DEFAULT_LANGUAGE=hi
SUPPORTED_LANGUAGES=hi,bn,ta,te

# Offline Mode (True for edge deployment)
OFFLINE_MODE=True

# Cloud Sync (False for offline-only)
ENABLE_CLOUD_SYNC=False
```

### Generating Secure Keys

```bash
# Generate DATABASE_KEY
python3 -c "import secrets; print(secrets.token_hex(16))"

# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## AI Models Setup

### Option 1: Download Pre-configured Models

```bash
python scripts/download_models.py
```

This downloads:
- Whisper Small (for STT)
- Llama 2 7B quantized (for reasoning)
- Multilingual sentence transformer

### Option 2: Use Bhashini API

If models are too large for your device, configure Bhashini:

```bash
# In .env
BHASHINI_API_KEY=your-api-key-here
BHASHINI_API_URL=https://api.bhashini.gov.in/v1
```

---

## Running the Server

### Development Mode
```bash
cd edge_server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode (with Gunicorn)
```bash
gunicorn edge_server.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

### Docker Mode
```bash
docker-compose up -d
```

### Check if Running
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "sakti-link-edge",
  "version": "1.0.0",
  "mode": "offline"
}
```

---

## Monitoring & Maintenance

### View Logs

**Docker:**
```bash
docker logs -f sakti-link-edge
```

**Systemd:**
```bash
sudo journalctl -u sakti-link -f
```

**Log Files:**
```bash
tail -f logs/edge_server.log
```

### Monitor System Resources

```bash
# CPU and Memory
htop

# Disk Space
df -h

# Database Size
du -sh data/sakti_link.db
```

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

### Metrics Endpoint

```bash
curl http://localhost:8000/api/v1/system/metrics
```

### Database Backup

```bash
# Stop server
sudo systemctl stop sakti-link  # or docker-compose down

# Backup database
cp data/sakti_link.db data/sakti_link_backup_$(date +%Y%m%d).db

# Restart server
sudo systemctl start sakti-link  # or docker-compose up -d
```

---

## Troubleshooting

### Server Won't Start

**Check logs:**
```bash
tail -n 100 logs/edge_server.log
```

**Common issues:**
- Port 8000 already in use: Change PORT in .env
- Redis not running: `sudo systemctl start redis-server`
- Database locked: Stop all instances, remove .db-shm and .db-wal files

### High Memory Usage

**If using full AI models:**
- Use quantized models (Q4_K_M)
- Enable model offloading
- Use Bhashini API instead of local models

**Check memory:**
```bash
free -h
```

### Audio Processing Errors

**Install missing codecs:**
```bash
sudo apt-get install ffmpeg libsndfile1 -y
```

### Database Errors

**Reset database (WARNING: Deletes all data):**
```bash
rm data/sakti_link.db
python scripts/init_db.py
```

---

## Performance Optimization

### For Low-End Devices (Raspberry Pi 3)

1. Use Bhashini API instead of local models
2. Reduce number of workers to 2
3. Enable aggressive caching
4. Limit concurrent requests

**In .env:**
```bash
OFFLINE_MODE=False  # Use cloud APIs
MAX_WORKERS=2
REDIS_CACHE_TTL=7200
```

### For High-Traffic Deployments

1. Use SSD storage
2. Increase worker count
3. Enable connection pooling
4. Use load balancer

---

## Security Best Practices

1. **Change default keys** in .env
2. **Restrict network access** using firewall
3. **Enable HTTPS** with reverse proxy (nginx)
4. **Regular backups** of database
5. **Update dependencies** regularly
6. **Monitor logs** for suspicious activity

---

## Updating the Server

### Docker
```bash
docker-compose down
git pull
docker-compose build
docker-compose up -d
```

### Manual
```bash
sudo systemctl stop sakti-link
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl start sakti-link
```

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/sakti-link-backend/issues
- Email: support@sakti-link.org
- Documentation: https://docs.sakti-link.org
