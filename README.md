<p align="center">
  <img src="https://raw.githubusercontent.com/Ishita-Si/Sakti-Link/main/docs/Screenshot%202026-01-21%20155644.png" width="100%" />
</p>

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

### Block 3: Cloud Layer
- Metadata synchronization
- Model updates
- Aggregated analytics
- Global marketplace metadata

  <p align="center">
  <img src="https://raw.githubusercontent.com/Ishita-Si/Sakti-Link/main/docs/Architecture.png" width="100%" />
</p>


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

### Cloud 
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



## Security

- All user data encrypted at rest using SQLCipher
- No raw audio or transcripts leave the edge server
- Anonymized IDs for all user interactions
- Optional cloud sync uses metadata only
- HTTPS/TLS for all API communication



## Performance Optimization

- Model quantization (4-bit) for low-memory devices
- Response caching with Redis
- Batch processing for multiple requests
- Lazy loading of AI models
- Connection pooling


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details



## Roadmap

- Phase 1: Core voice interaction and intent routing
- Phase 2: Learning modules and skill swap
- Phase 3: Micro-gig marketplace
- Phase 4: Legal awareness AI
- Phase 5: Cloud synchronization
-  Phase 6: Multi-edge server federation
-  Phase 7: Mobile app integration

## Acknowledgments

- AI4Bharat for Indic language models
- Bhashini for speech services
- Meta for Llama models
- Open-source community
