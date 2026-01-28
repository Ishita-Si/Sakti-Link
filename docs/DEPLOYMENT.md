# Sakti-Link Edge Server Deployment Guide

## Table of Contents
1. [Hardware Requirements](#hardware-requirements)
2. [Software Prerequisites](#software-prerequisites)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Running the Server](#running-the-server)

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


### Manual Installation

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



### Database Backup

```bash
# Stop server
sudo systemctl stop sakti-link  # or docker-compose down

# Backup database
cp data/sakti_link.db data/sakti_link_backup_$(date +%Y%m%d).db

# Restart server
sudo systemctl start sakti-link  # or docker-compose up -d
```

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

### For Low-End Devices 

1. Use Bhashini API instead of local models
2. Reduce number of workers to 2
3. Enable aggressive caching
4. Limit concurrent requests

---

## Support

For issues and questions:
- Email: 24cs2019@rgipt.ac.in

