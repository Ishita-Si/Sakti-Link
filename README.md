# Sakti-Link Backend

Voice-first, offline-first AI platform for women's empowerment through skilling, earning, and legal awareness.

## Architecture Overview

This backend implements a three-layer architecture:

### Block 1: User Device (Low-End Smartphone)
- Lightweight mobile client (not included in this repo)
- Voice capture and playback
- Local caching
- Communicates with Edge Server

### Block 2: Community Edge Server (THIS REPO)
- Runs on low-cost hardware (Raspberry Pi, etc.)
- Offline-first operation
- Local AI inference
- Encrypted data storage
- Core services: Learning, Earning (Micro-gigs), Legal Help

### Block 3: Optional Cloud Layer
- Metadata synchronization
- Model updates
- Aggregated analytics
- Global marketplace metadata

## Technology Stack

### Edge Server
- **Python 3.9+** - Main backend language
- **FastAPI** - REST API framework
- **SQLite** - Local database (encrypted)
- **SQLCipher** - Database encryption
- **Redis** - Caching and queue management
- **Celery** - Background task processing

### AI/ML Models
- **Bhashini API** - Speech-to-Text & Text-to-Speech
- **AI4Bharat IndicWhisper** - ASR for Indian languages
- **IndicTrans2** - Translation
- **Llama (quantized)** - Intent understanding and reasoning
- **Sentence Transformers** - Semantic search

### Cloud (Optional)
- **FastAPI** - Cloud API
- **PostgreSQL** - Cloud database
- **Redis** - Cloud caching
- **MinIO/S3** - Model storage

## Project Structure

```
sakti-link-backend/
├── edge_server/              # Community Edge Server (Block 2)
│   ├── api/                  # REST API endpoints
│   ├── core/                 # Core business logic
│   ├── models/               # Data models
│   ├── services/             # Service layer
│   ├── ai/                   # AI model integration
│   ├── db/                   # Database management
│   └── config/               # Configuration
├── cloud_server/             # Optional Cloud Layer (Block 3)
│   ├── api/                  # Cloud API endpoints
│   ├── services/             # Cloud services
│   └── analytics/            # Analytics engine
├── shared/                   # Shared utilities
│   ├── encryption/           # Encryption utilities
│   ├── models/               # Shared models
│   └── utils/                # Common utilities
├── scripts/                  # Deployment & setup scripts
├── tests/                    # Test suites
└── docs/                     # Documentation

```

## Features Implemented

### Core Services
1. **Voice Interaction** - STT/TTS with Bhashini integration
2. **Intent Routing** - Learn, Earn, Legal Help
3. **Nano-Learning** - 2-minute audio modules
4. **Skill-Swap Time Bank** - Credit system for teaching/learning
5. **Micro-Gig Marketplace** - Local job matching
6. **Legal Awareness** - Voice-based guidance
7. **Privacy-First Design** - Local encryption, anonymization

### Technical Features
- Offline-first operation
- Encrypted local database
- Multi-language support (Hindi, Bengali, Tamil, Telugu, etc.)
- Low-bandwidth optimization
- Background sync when online
- Metadata-only cloud sync

## Quick Start

### Prerequisites
```bash
# Python 3.9+
python3 --version

# Redis (for caching)
sudo apt-get install redis-server

# SQLCipher (for encrypted database)
sudo apt-get install sqlcipher libsqlcipher-dev
```

### Installation

1. Clone the repository
```bash
git clone <repo-url>
cd sakti-link-backend
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database
```bash
python scripts/init_db.py
```

5. Download AI models
```bash
python scripts/download_models.py
```

### Running the Edge Server

```bash
# Development mode
cd edge_server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode (with workers)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Running the Cloud Server (Optional)

```bash
cd cloud_server
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## API Documentation

Once the server is running, access:
- **Edge Server API Docs**: http://localhost:8000/docs
- **Cloud Server API Docs**: http://localhost:8001/docs

## Key API Endpoints

### Edge Server

#### Voice Interaction
- `POST /api/v1/voice/process` - Process voice input
- `POST /api/v1/voice/synthesize` - Text to speech

#### Learning
- `GET /api/v1/learning/modules` - List learning modules
- `POST /api/v1/learning/progress` - Update learning progress
- `GET /api/v1/learning/credits` - Get user credits

#### Earning (Micro-Gigs)
- `GET /api/v1/gigs/available` - List available gigs
- `POST /api/v1/gigs/apply` - Apply for a gig
- `GET /api/v1/gigs/user` - User's gig history

#### Legal Help
- `POST /api/v1/legal/query` - Ask legal question
- `GET /api/v1/legal/topics` - List legal topics

#### Skill Swap
- `POST /api/v1/skills/teach` - Register skill to teach
- `POST /api/v1/skills/learn` - Request to learn skill
- `GET /api/v1/skills/marketplace` - Browse skills

### Cloud Server

#### Sync
- `POST /api/v1/sync/metadata` - Sync edge server metadata
- `GET /api/v1/sync/updates` - Get model updates

#### Analytics
- `GET /api/v1/analytics/usage` - Usage statistics
- `GET /api/v1/analytics/impact` - Impact metrics

## Configuration

### Edge Server Configuration (`edge_server/config/settings.py`)

```python
# Database
DATABASE_PATH = "data/sakti_link.db"
DATABASE_KEY = "your-encryption-key"

# AI Models
WHISPER_MODEL = "ai4bharat/indicwhisper-medium"
LLAMA_MODEL = "llama-2-7b-chat-q4"
TTS_ENGINE = "bhashini"

# Languages
SUPPORTED_LANGUAGES = ["hi", "bn", "ta", "te", "mr", "gu"]

# Offline Mode
OFFLINE_MODE = True
SYNC_INTERVAL = 3600  # seconds
```

## Deployment

### Raspberry Pi Setup

```bash
# Install on Raspberry Pi 4 (4GB+ RAM recommended)
sudo apt-get update
sudo apt-get install python3-pip redis-server nginx

# Clone and setup
git clone <repo-url>
cd sakti-link-backend
pip3 install -r requirements-edge.txt

# Setup as systemd service
sudo cp scripts/sakti-link-edge.service /etc/systemd/system/
sudo systemctl enable sakti-link-edge
sudo systemctl start sakti-link-edge
```

### Docker Deployment

```bash
# Build edge server image
docker build -f Dockerfile.edge -t sakti-link-edge .

# Run container
docker run -d -p 8000:8000 \
  -v ./data:/app/data \
  -v ./models:/app/models \
  --name sakti-link-edge \
  sakti-link-edge
```

## Security

- All user data encrypted at rest using SQLCipher
- No raw audio or transcripts leave the edge server
- Anonymized IDs for all user interactions
- Optional cloud sync uses metadata only
- HTTPS/TLS for all API communication

## Testing

```bash
# Run all tests
pytest

# Run edge server tests
pytest tests/edge_server/

# Run cloud server tests
pytest tests/cloud_server/

# Run with coverage
pytest --cov=edge_server --cov=cloud_server
```

## Performance Optimization

- Model quantization (4-bit) for low-memory devices
- Response caching with Redis
- Batch processing for multiple requests
- Lazy loading of AI models
- Connection pooling

## Monitoring

```bash
# View logs
tail -f logs/edge_server.log

# Monitor system resources
htop

# Redis monitoring
redis-cli monitor
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: <repo-url>/issues
- Email: support@sakti-link.org

## Roadmap

- [ ] Phase 1: Core voice interaction and intent routing
- [ ] Phase 2: Learning modules and skill swap
- [ ] Phase 3: Micro-gig marketplace
- [ ] Phase 4: Legal awareness AI
- [ ] Phase 5: Cloud synchronization
- [ ] Phase 6: Multi-edge server federation
- [ ] Phase 7: Mobile app integration

## Acknowledgments

- AI4Bharat for Indic language models
- Bhashini for speech services
- Meta for Llama models
- Open-source community
