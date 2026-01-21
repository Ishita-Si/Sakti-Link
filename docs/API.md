# Sakti-Link Edge Server API Documentation

## Overview

The Sakti-Link Edge Server provides a voice-first, offline-first API for women's empowerment through learning, earning, and legal awareness.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, users are identified by device fingerprint. No authentication token required for edge server (runs locally).

## API Endpoints

### 1. Voice Processing

#### Process Voice Input
**POST** `/api/v1/voice/process`

Main endpoint for voice interactions. Handles: STT → Intent Understanding → Response Generation → TTS

**Request Body:**
```json
{
  "audio_base64": "base64_encoded_audio_data",
  "language": "hi",
  "device_fingerprint": "unique_device_id"
}
```

**Response:**
```json
{
  "success": true,
  "transcript": "मुझे सिलाई सीखनी है",
  "intent": {
    "intent": "skill_swap",
    "confidence": 0.85,
    "entities": {}
  },
  "response_text": "बहुत अच्छे! सिलाई सीखने के लिए...",
  "response_audio_base64": "base64_encoded_audio_response",
  "next_action": "skill_swap",
  "metadata": {
    "confidence": 0.85,
    "processing_time": "0.5s"
  }
}
```

#### Text to Speech
**POST** `/api/v1/voice/synthesize`

Convert text to speech audio.

**Request Body:**
```json
{
  "text": "नमस्ते! मैं सक्ति-लिंक हूँ",
  "language": "hi"
}
```

**Response:** Audio file (WAV format)

#### Get Supported Languages
**GET** `/api/v1/voice/languages`

**Response:**
```json
{
  "languages": [
    {"code": "hi", "name": "हिंदी (Hindi)"},
    {"code": "bn", "name": "বাংলা (Bengali)"},
    ...
  ]
}
```

---

### 2. Learning

#### List Learning Modules
**POST** `/api/v1/learning/modules/list`

**Request Body:**
```json
{
  "category": "financial_literacy",
  "language": "hi",
  "user_id": "user_abc123"
}
```

**Response:** Text response with available modules

#### Start Learning Module
**POST** `/api/v1/learning/modules/{module_id}/start`

**Query Parameters:**
- `user_id`: string (required)

**Response:**
```json
{
  "success": true,
  "module": {
    "id": 1,
    "title": "बेसिक बैंकिंग और बचत",
    "duration": 120,
    "audio_path": "modules/banking_basics_hi.mp3",
    "transcript": "..."
  }
}
```

#### Complete Learning Module
**POST** `/api/v1/learning/modules/{module_id}/complete`

**Query Parameters:**
- `user_id`: string (required)

**Response:**
```json
{
  "success": true,
  "credits_earned": 2,
  "message": "Module completed successfully"
}
```

#### Get User Credits
**GET** `/api/v1/learning/credits/{user_id}`

**Response:**
```json
{
  "user_id": "user_abc123",
  "credits": 15
}
```

---

### 3. Gigs (Micro-gig Marketplace)

#### Get Available Gigs
**GET** `/api/v1/gigs/available`

**Query Parameters:**
- `user_id`: string (required)
- `language`: string (default: "hi")

**Response:**
```json
{
  "gigs": [
    {
      "id": 1,
      "title": "कपड़े सिलने का काम",
      "payment": 500,
      "location": "रायबरेली"
    },
    ...
  ]
}
```

#### Apply for Gig
**POST** `/api/v1/gigs/{gig_id}/apply`

**Query Parameters:**
- `user_id`: string (required)

**Response:**
```json
{
  "success": true,
  "application_id": 123
}
```

#### Get User's Gig Applications
**GET** `/api/v1/gigs/user/{user_id}`

**Response:**
```json
{
  "applications": [
    {
      "gig_id": 1,
      "status": "pending",
      "applied_at": "2025-01-20T10:30:00"
    },
    ...
  ]
}
```

---

### 4. Legal Awareness

#### Ask Legal Question
**POST** `/api/v1/legal/query`

**Request Body:**
```json
{
  "user_id": "user_abc123",
  "query": "न्यूनतम मजदूरी क्या है?",
  "language": "hi"
}
```

**Response:**
```json
{
  "response": "न्यूनतम मजदूरी का अर्थ है... [legal information + disclaimer]"
}
```

#### Get Legal Topics
**GET** `/api/v1/legal/topics`

**Query Parameters:**
- `language`: string (default: "hi")

**Response:**
```json
{
  "topics": [
    {
      "id": 1,
      "name": "न्यूनतम मजदूरी",
      "description": "काम के लिए न्यूनतम मजदूरी के अधिकार",
      "category": "labor_rights"
    },
    ...
  ]
}
```

---

### 5. Skills (Skill-Swap Time Bank)

#### Register Skill to Teach
**POST** `/api/v1/skills/teach`

**Request Body:**
```json
{
  "user_id": "user_abc123",
  "skill_name": "सिलाई",
  "proficiency": 4
}
```

**Response:**
```json
{
  "success": true,
  "skill_id": 5,
  "user_skill_id": 123
}
```

#### Register Interest in Learning Skill
**POST** `/api/v1/skills/learn`

**Request Body:**
```json
{
  "user_id": "user_abc123",
  "skill_id": 5
}
```

**Response:**
```json
{
  "success": true,
  "user_skill_id": 124
}
```

#### Get Skill Marketplace
**GET** `/api/v1/skills/marketplace`

**Query Parameters:**
- `language`: string (default: "hi")

**Response:**
```json
{
  "skills": [
    {
      "skill_id": 1,
      "skill_name": "सिलाई",
      "category": "crafts",
      "proficiency": 4,
      "available_hours": {"monday": ["10:00-12:00"]}
    },
    ...
  ]
}
```

---

### 6. System

#### Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "sakti-link-edge",
  "version": "1.0.0",
  "mode": "offline"
}
```

#### System Status
**GET** `/api/v1/system/status`

**Response:**
```json
{
  "status": "operational",
  "mode": "offline",
  "version": "1.0.0",
  "supported_languages": ["hi", "bn", "ta", ...]
}
```

#### Get System Metrics
**GET** `/api/v1/system/metrics`

**Response:**
```json
{
  "period": "24h",
  "metrics": {
    "voice_interaction": {"total": 150, "count": 150},
    "learning_sessions": {"total": 45, "count": 45}
  },
  "timestamp": "2025-01-21T10:00:00"
}
```

#### Get Sync Status
**GET** `/api/v1/system/sync/status`

**Response:**
```json
{
  "enabled": false,
  "last_sync": null,
  "pending_syncs": 0,
  "cloud_url": null
}
```

#### Trigger Manual Sync
**POST** `/api/v1/system/sync/trigger`

**Response:**
```json
{
  "success": true,
  "message": "Sync initiated"
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error

---

## Rate Limiting

Currently no rate limiting on edge server (local deployment).

---

## Privacy & Security

- All user data is anonymized with hashed device fingerprints
- No personal identifiable information stored
- Audio/transcripts not uploaded to cloud
- All data encrypted at rest using SQLCipher
- Metadata-only cloud sync (when enabled)

---

## Language Support

Supported languages: Hindi (hi), Bengali (bn), Tamil (ta), Telugu (te), Marathi (mr), Gujarati (gu), Kannada (kn), Malayalam (ml), Punjabi (pa), Odia (or)

All voice responses are in the requested language.
