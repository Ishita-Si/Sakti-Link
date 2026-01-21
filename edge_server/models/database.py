"""
Database models for Sakti-Link Edge Server
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from edge_server.db.database import Base
import uuid


def generate_anonymous_id():
    """Generate anonymous user ID"""
    return f"user_{uuid.uuid4().hex[:16]}"


class User(Base):
    """User model - anonymized"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_anonymous_id)
    language_preference = Column(String, default="hi")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Privacy: No personal identifiable information stored
    # Device fingerprint for session management only
    device_fingerprint = Column(String, unique=True, index=True)
    
    # Relationships
    learning_progress = relationship("LearningProgress", back_populates="user")
    skills = relationship("UserSkill", back_populates="user")
    gig_applications = relationship("GigApplication", back_populates="user")
    legal_queries = relationship("LegalQuery", back_populates="user")
    credits = relationship("CreditTransaction", back_populates="user")


class LearningModule(Base):
    """Learning content modules"""
    __tablename__ = "learning_modules"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # financial_literacy, vocational_skills, digital_safety
    language = Column(String, nullable=False)
    duration = Column(Integer)  # seconds
    audio_path = Column(String)  # local path to audio file
    transcript = Column(Text)
    difficulty_level = Column(Integer, default=1)  # 1-5
    credit_cost = Column(Integer, default=3)
    tags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    progress_records = relationship("LearningProgress", back_populates="module")


class LearningProgress(Base):
    """User learning progress"""
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=False)
    status = Column(String, default="not_started")  # not_started, in_progress, completed
    progress_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    credits_earned = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="learning_progress")
    module = relationship("LearningModule", back_populates="progress_records")


class Skill(Base):
    """Available skills in the system"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    language = Column(String, default="hi")
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_skills = relationship("UserSkill", back_populates="skill")


class UserSkill(Base):
    """Skills that users can teach or want to learn"""
    __tablename__ = "user_skills"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    skill_type = Column(String, nullable=False)  # teach, learn
    proficiency_level = Column(Integer, default=1)  # 1-5
    available_hours = Column(JSON)  # {"monday": ["10:00-12:00"], ...}
    location = Column(String)  # area/village name
    status = Column(String, default="active")  # active, paused, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="user_skills")


class CreditTransaction(Base):
    """Time-bank credit transactions"""
    __tablename__ = "credit_transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # positive for earning, negative for spending
    transaction_type = Column(String, nullable=False)  # teach, learn, initial, bonus
    description = Column(String)
    related_module_id = Column(Integer, ForeignKey("learning_modules.id"))
    related_skill_id = Column(Integer, ForeignKey("skills.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="credits")


class Gig(Base):
    """Micro-gig opportunities"""
    __tablename__ = "gigs"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # household, artisan, care, digital, other
    location = Column(String)
    location_lat = Column(Float)
    location_lon = Column(Float)
    duration = Column(Integer)  # hours
    payment = Column(Float)
    payment_currency = Column(String, default="INR")
    required_skills = Column(JSON)
    time_flexibility = Column(String)  # morning, afternoon, evening, flexible
    status = Column(String, default="open")  # open, filled, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    applications = relationship("GigApplication", back_populates="gig")


class GigApplication(Base):
    """User applications for gigs"""
    __tablename__ = "gig_applications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    gig_id = Column(Integer, ForeignKey("gigs.id"), nullable=False)
    status = Column(String, default="pending")  # pending, accepted, rejected, completed
    applied_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    rating = Column(Integer)  # 1-5
    feedback = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="gig_applications")
    gig = relationship("Gig", back_populates="applications")


class LegalTopic(Base):
    """Legal information topics"""
    __tablename__ = "legal_topics"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    language = Column(String, default="hi")
    content = Column(Text)  # Main legal information
    audio_path = Column(String)  # Path to audio explanation
    related_laws = Column(JSON)
    helpful_resources = Column(JSON)
    is_active = Column(Boolean, default=True)


class LegalQuery(Base):
    """Anonymized legal queries from users"""
    __tablename__ = "legal_queries"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    query_hash = Column(String, index=True)  # Hashed query for privacy
    topic_category = Column(String)
    language = Column(String)
    response_summary = Column(Text)  # Summarized response, no raw transcript
    was_helpful = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="legal_queries")


class SyncMetadata(Base):
    """Metadata for cloud synchronization"""
    __tablename__ = "sync_metadata"
    
    id = Column(Integer, primary_key=True)
    entity_type = Column(String, nullable=False)  # user, gig, module, etc.
    entity_id = Column(String, nullable=False)
    last_synced = Column(DateTime)
    sync_status = Column(String, default="pending")  # pending, synced, failed
    sync_attempts = Column(Integer, default=0)
    metadata = Column(JSON)  # Anonymized metadata only
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemMetrics(Base):
    """System usage metrics (anonymized)"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True)
    metric_type = Column(String, nullable=False)  # voice_queries, learning_sessions, etc.
    metric_value = Column(Float)
    language = Column(String)
    category = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON)
