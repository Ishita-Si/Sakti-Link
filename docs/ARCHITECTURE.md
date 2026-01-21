# Sakti-Link Architecture Documentation

## System Overview

Sakti-Link is a voice-first, offline-first AI platform designed for women's empowerment through skilling, earning opportunities, and legal awareness. The system consists of three main layers:

1. **User Device Layer**: Low-end smartphones with voice interface
2. **Community Edge Server**: Local AI processing hub
3. **Optional Cloud Layer**: Metadata sync and analytics

---

## Architecture Principles

### 1. Privacy-First Design
- All processing happens locally on edge servers
- No raw audio or transcripts uploaded to cloud
- Anonymous user identification (hashed device fingerprints)
- Encrypted data at rest (SQLCipher)
- Metadata-only cloud synchronization

### 2. Offline-First Operation
- Full functionality without internet
- Local AI model inference
- Cached content delivery
- Background sync when online
- Resilient to network failures

### 3. Voice-First Interface
- No reading or typing required
- Multilingual speech recognition (10+ Indian languages)
- Natural conversation flow
- Audio-based learning modules
- Voice-guided workflows

### 4. Low-Resource Optimization
- Quantized AI models (4-bit)
- Runs on Raspberry Pi hardware
- Minimal bandwidth usage
- Efficient database queries
- Lazy loading of resources

---

## Detailed Component Architecture

### Layer 1: User Device

**Components:**
- Lightweight mobile app (React Native / Flutter)
- Voice capture interface
- Audio playback
- Local cache storage
- Network detection

**Data Flow:**
1. User speaks into microphone
2. Audio captured and compressed
3. Sent to Edge Server via local network
4. Response audio received and played
5. Conversation state cached locally

**Technology:**
- Audio: WebRTC / native audio APIs
- Storage: AsyncStorage / SQLite Lite
- Network: HTTP/2 with retry logic
- UI: Minimal, voice-centric design

---

### Layer 2: Community Edge Server (Core)

This is the heart of the system, running on low-cost hardware in community centers.

#### 2.1 API Layer (`edge_server/api/`)

**FastAPI Application:**
- RESTful API endpoints
- WebSocket support (future)
- Request validation (Pydantic)
- Error handling
- CORS middleware

**Key Endpoints:**
- `/api/v1/voice/*` - Voice processing
- `/api/v1/learning/*` - Learning modules
- `/api/v1/gigs/*` - Micro-gig marketplace
- `/api/v1/legal/*` - Legal awareness
- `/api/v1/skills/*` - Skill-swap
- `/api/v1/system/*` - System management

#### 2.2 AI/ML Layer (`edge_server/ai/`)

**Model Manager:**
- Lazy loading of models
- Memory management
- Model quantization
- Fallback to API when needed

**Models:**

1. **Speech-to-Text**
   - Primary: AI4Bharat IndicWhisper
   - Fallback: Bhashini API
   - Languages: 10+ Indian languages
   - Size: ~500MB (small model)

2. **Language Model**
   - Primary: Llama 2 7B (4-bit quantized)
   - Purpose: Intent understanding, response generation
   - Size: ~4GB (quantized)
   - Inference: llama-cpp-python

3. **Text-to-Speech**
   - Primary: Bhashini API
   - Fallback: gTTS
   - Natural voice synthesis

4. **Semantic Search**
   - Model: Multilingual Sentence Transformer
   - Purpose: Skill matching, content search
   - Size: ~500MB

**Processing Pipeline:**
```
Audio Input
    ↓
Speech-to-Text (Whisper/Bhashini)
    ↓
Intent Classification (Llama/Rule-based)
    ↓
Service Router
    ↓
├─ Learning Service
├─ Gig Service
├─ Legal Service
└─ Skill Service
    ↓
Response Generation (Llama/Templates)
    ↓
Text-to-Speech (Bhashini)
    ↓
Audio Output
```

#### 2.3 Service Layer (`edge_server/services/`)

**Learning Service:**
- Nano-learning module delivery
- Progress tracking
- Credit management
- Content recommendation

**Gig Service:**
- Micro-gig listings
- Location-based matching
- Application tracking
- Payment status

**Legal Service:**
- Topic detection
- Information retrieval
- AI-powered Q&A
- Privacy-preserving logging

**Skill Service:**
- Time-bank credit system
- Skill registration (teach/learn)
- Matching algorithm
- Session completion tracking

#### 2.4 Database Layer (`edge_server/db/`)

**Technology:** SQLite + SQLCipher (encryption)

**Key Tables:**

- `users` - Anonymous user profiles
- `learning_modules` - Educational content
- `learning_progress` - User progress tracking
- `skills` - Available skills
- `user_skills` - User skill listings
- `credit_transactions` - Time-bank ledger
- `gigs` - Job listings
- `gig_applications` - Application tracking
- `legal_topics` - Legal information
- `legal_queries` - Anonymized queries
- `sync_metadata` - Cloud sync tracking
- `system_metrics` - Usage analytics

**Schema Design Principles:**
- Normalized for data integrity
- Indexed for query performance
- Encrypted at rest
- No PII stored
- Audit trail for transactions

#### 2.5 Core Layer (`edge_server/core/`)

**Configuration Management:**
- Environment variables
- Feature flags
- Language settings
- Model configurations

**Utilities:**
- Encryption helpers
- Anonymization functions
- Cache management
- Error handling

---

### Layer 3: Optional Cloud Server

**Purpose:**
- Model distribution
- Metadata aggregation
- Impact analytics
- Global marketplace federation

**Key Features:**

1. **Model Repository**
   - Updated AI models
   - Language packs
   - Content updates
   - Version control

2. **Analytics Engine**
   - Anonymized usage metrics
   - Impact assessment
   - Trend analysis
   - Reporting dashboards

3. **Federation Service**
   - Connect multiple edge servers
   - Global gig marketplace
   - Skill-swap across communities
   - Best practice sharing

**Technology Stack:**
- FastAPI (API)
- PostgreSQL (Database)
- Redis (Caching)
- MinIO/S3 (Model storage)
- TimescaleDB (Time-series analytics)

---

## Data Flow Diagrams

### Voice Interaction Flow

```
User Device                 Edge Server                     AI Models
    |                           |                               |
    |-- Audio Recording -->     |                               |
    |                           |-- Extract Audio -->           |
    |                           |                   STT Model --|
    |                           |<-- Transcript ----------------| 
    |                           |                               |
    |                           |-- Understand Intent -->       |
    |                           |                   LLM --------|
    |                           |<-- Intent + Entities ---------| 
    |                           |                               |
    |                           |-- Process Request -->         |
    |                           |   (Service Layer)             |
    |                           |<-- Response Text -------------|
    |                           |                               |
    |                           |-- Generate Speech -->         |
    |                           |                   TTS Model --|
    |                           |<-- Audio Response ------------|
    |<-- Audio Response --------|                               |
    |                           |                               |
    |   Play Audio              |                               |
```

### Learning Module Flow

```
User Request
    ↓
Voice API
    ↓
Learning Service
    ↓
├─ Check User Credits
├─ Query Available Modules
├─ Filter by Language/Category
├─ Get User Progress
└─ Deduct Credits (if starting)
    ↓
Database
    ↓
Response to User
```

### Skill-Swap Flow

```
Teaching Request          Learning Request
    ↓                         ↓
Skill Service             Skill Service
    ↓                         ↓
Register Skill            Find Teachers
    ↓                         ↓
+5 Credits                -3 Credits
    ↓                         ↓
Time Bank                 Time Bank
```

---

## Security Architecture

### Authentication & Authorization

**User Identification:**
- Device fingerprint (hashed)
- No passwords or personal data
- Session tokens for API calls
- JWT for cloud sync (future)

**Data Protection:**
- AES-256 encryption at rest
- TLS 1.3 for transport
- No raw audio stored
- Anonymized query hashing

### Privacy Measures

1. **Local Processing:**
   - All AI inference on edge
   - No cloud dependencies for core features

2. **Anonymization:**
   - Hashed user IDs
   - Hashed query logs
   - No voice recordings stored

3. **Consent:**
   - Explicit opt-in for cloud sync
   - User control over data
   - Clear privacy policy

4. **Audit:**
   - All transactions logged
   - No retroactive data access
   - Data retention policies

---

## Scalability Strategy

### Horizontal Scaling

1. **Multiple Edge Servers:**
   - Deploy in multiple communities
   - Federation protocol for inter-server communication
   - Shared global marketplace

2. **Load Distribution:**
   - Round-robin for voice requests
   - Sticky sessions for conversations
   - Background jobs for heavy tasks

### Vertical Scaling

1. **Hardware Upgrades:**
   - Raspberry Pi 4 → Intel NUC → Server
   - More RAM for larger models
   - SSD for faster database

2. **Model Optimization:**
   - Progressive quantization (8-bit → 4-bit)
   - Model pruning
   - Distillation for smaller models

---

## Deployment Topologies

### Topology 1: Single Community (50-200 users)
```
[Community Center]
    ├─ Edge Server (Raspberry Pi 4)
    ├─ Router/WiFi Access Point
    └─ [Users with smartphones]
```

### Topology 2: Multi-Community Federation (500+ users)
```
[Community 1]          [Community 2]          [Community 3]
 Edge Server ─────────── Edge Server ─────────── Edge Server
      │                       │                       │
      └───────────────────────┴───────────────────────┘
                              │
                         [Cloud Server]
                     (Optional Aggregation)
```

### Topology 3: Hybrid (Online + Offline)
```
[Community Center]
    ├─ Edge Server (Primary)
    ├─ Cloud API (Fallback for models)
    └─ Users
         ├─ Offline-capable app
         └─ Cached content
```

---

## Technology Choices Rationale

### Why SQLite over PostgreSQL?
- Embedded, no server required
- Perfect for edge deployment
- Encryption support (SQLCipher)
- Low resource usage
- Simple backup/restore

### Why Llama 2 over GPT-4?
- Open-source, no API costs
- Runs locally (privacy)
- Can be quantized for edge
- Good multilingual support with fine-tuning

### Why FastAPI over Flask?
- Async/await support (better concurrency)
- Automatic API documentation
- Type hints with Pydantic
- Modern, fast, and lightweight

### Why Bhashini?
- Government-backed Indian language platform
- Free API access
- Optimized for Indian accents
- Multiple language support

---

## Performance Benchmarks

### Expected Performance (Raspberry Pi 4, 4GB)

- **Voice Processing:** 1-2 seconds end-to-end
- **STT Latency:** 500-800ms
- **Intent Classification:** 100-200ms
- **Response Generation:** 200-500ms
- **TTS Latency:** 300-500ms
- **Database Queries:** <50ms
- **Concurrent Users:** 10-20 simultaneous
- **Daily Users:** 200-300

### Resource Usage

- **Memory:** 1.5-2.5GB (with AI models loaded)
- **Storage:** 8-12GB (models + data)
- **CPU:** 40-60% during processing
- **Network:** <1KB per voice interaction (local)

---

## Future Enhancements

### Phase 1 (Complete - Current)
- ✅ Voice-first interface
- ✅ Offline-first operation
- ✅ Learning modules
- ✅ Micro-gig marketplace
- ✅ Legal awareness

### Phase 2 (Next 6 months)
- WebSocket for real-time conversations
- Mobile app development (Android)
- Enhanced AI with fine-tuned models
- Multi-modal input (image + voice)
- Advanced skill matching algorithm

### Phase 3 (6-12 months)
- Federation protocol implementation
- iOS app development
- Computer vision for document scanning
- WhatsApp/SMS integration
- Regional language content expansion

### Phase 4 (12+ months)
- Blockchain-based time bank
- P2P skill exchange without server
- AI-powered mentor matching
- Gamification and achievements
- Integration with government schemes

---

## Monitoring & Observability

### Key Metrics

**System Health:**
- CPU/Memory/Disk usage
- API response times
- Error rates
- Model inference latency

**Business Metrics:**
- Daily active users
- Voice interactions
- Learning completions
- Gig applications
- Skill exchanges

**Tools:**
- Prometheus (metrics collection)
- Grafana (visualization)
- Loguru (logging)
- Custom analytics dashboard

---

## Disaster Recovery

### Backup Strategy

1. **Database:**
   - Daily automated backups
   - Encrypted backup storage
   - Off-site backup (optional)
   - 30-day retention

2. **Models:**
   - Version-controlled in cloud
   - Easy re-download
   - Fallback to API

3. **Configuration:**
   - Git repository
   - Environment variable backup

### Recovery Procedures

1. **Hardware Failure:**
   - Restore from backup to new device
   - Reconfigure network
   - Test all services

2. **Data Corruption:**
   - Restore last known good backup
   - Replay transactions if possible
   - Notify users of data loss

3. **Model Issues:**
   - Fallback to API
   - Download fresh models
   - Rollback to previous version

---

## Conclusion

Sakti-Link's architecture prioritizes privacy, accessibility, and resilience. By processing everything locally on edge servers and supporting offline-first operation, the system remains functional even in low-connectivity environments. The voice-first interface eliminates literacy barriers, while the modular design allows for continuous improvement and scalability.
