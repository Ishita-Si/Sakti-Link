"""
Initialize Sakti-Link database with sample data
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from edge_server.db.database import init_db, get_db
from edge_server.models.database import (
    LearningModule, Skill, Gig, LegalTopic
)
from datetime import datetime, timedelta


async def create_sample_learning_modules():
    """Create sample learning modules"""
    async with get_db() as db:
        modules = [
            LearningModule(
                title="बेसिक बैंकिंग और बचत",
                description="बैंक खाता कैसे खोलें और पैसे बचाएं",
                category="financial_literacy",
                language="hi",
                duration=120,
                audio_path="modules/banking_basics_hi.mp3",
                transcript="बैंक खाता खोलना बहुत आसान है...",
                difficulty_level=1,
                credit_cost=3,
                tags=["banking", "savings", "financial"]
            ),
            LearningModule(
                title="डिजिटल भुगतान की सुरक्षा",
                description="UPI और डिजिटल वॉलेट का सुरक्षित उपयोग",
                category="digital_safety",
                language="hi",
                duration=120,
                audio_path="modules/digital_payments_hi.mp3",
                transcript="डिजिटल भुगतान करते समय सावधानियां...",
                difficulty_level=2,
                credit_cost=3,
                tags=["digital", "payments", "safety"]
            ),
            LearningModule(
                title="सिलाई मशीन का उपयोग",
                description="बेसिक सिलाई तकनीक सीखें",
                category="vocational_skills",
                language="hi",
                duration=120,
                audio_path="modules/sewing_basics_hi.mp3",
                transcript="सिलाई मशीन को कैसे चलाएं...",
                difficulty_level=1,
                credit_cost=3,
                tags=["sewing", "tailoring", "vocational"]
            ),
        ]
        
        for module in modules:
            db.add(module)
        
        await db.commit()
        print(f"Created {len(modules)} learning modules")


async def create_sample_skills():
    """Create sample skills"""
    async with get_db() as db:
        skills = [
            Skill(name="सिलाई", description="कपड़े सिलना", category="crafts", language="hi"),
            Skill(name="कढ़ाई", description="कपड़े पर कढ़ाई करना", category="crafts", language="hi"),
            Skill(name="खाना बनाना", description="पारंपरिक व्यंजन", category="cooking", language="hi"),
            Skill(name="मोबाइल रिपेयर", description="बेसिक मोबाइल मरम्मत", category="technical", language="hi"),
            Skill(name="मेहंदी", description="मेहंदी लगाना", category="beauty", language="hi"),
        ]
        
        for skill in skills:
            db.add(skill)
        
        await db.commit()
        print(f"Created {len(skills)} skills")


async def create_sample_gigs():
    """Create sample gigs"""
    async with get_db() as db:
        gigs = [
            Gig(
                title="कपड़े सिलने का काम",
                description="10 सूट सिलने हैं",
                category="artisan",
                location="रायबरेली",
                duration=8,
                payment=500,
                required_skills=["सिलाई"],
                time_flexibility="flexible",
                status="open",
                expires_at=datetime.utcnow() + timedelta(days=7)
            ),
            Gig(
                title="बच्चों की देखभाल",
                description="शाम 4-8 बजे बच्चे देखना",
                category="care",
                location="रायबरेली",
                duration=4,
                payment=200,
                required_skills=[],
                time_flexibility="evening",
                status="open",
                expires_at=datetime.utcnow() + timedelta(days=3)
            ),
            Gig(
                title="डाटा एंट्री",
                description="100 फॉर्म्स को कंप्यूटर में भरना",
                category="digital",
                location="रायबरेली",
                duration=6,
                payment=300,
                required_skills=[],
                time_flexibility="flexible",
                status="open",
                expires_at=datetime.utcnow() + timedelta(days=5)
            ),
        ]
        
        for gig in gigs:
            db.add(gig)
        
        await db.commit()
        print(f"Created {len(gigs)} gigs")


async def create_sample_legal_topics():
    """Create sample legal topics"""
    async with get_db() as db:
        topics = [
            LegalTopic(
                name="न्यूनतम मजदूरी",
                description="काम के लिए न्यूनतम मजदूरी के अधिकार",
                category="labor_rights",
                language="hi",
                content="हर काम करने वाली महिला को न्यूनतम मजदूरी पाने का अधिकार है। वर्तमान में...",
                related_laws=["Minimum Wages Act, 1948"],
                helpful_resources=["Labour Department Helpline: 1800-123-4567"]
            ),
            LegalTopic(
                name="घरेलू हिंसा",
                description="घरेलू हिंसा से संरक्षण",
                category="domestic_violence",
                language="hi",
                content="घरेलू हिंसा से महिला संरक्षण अधिनियम 2005 के तहत...",
                related_laws=["Protection of Women from Domestic Violence Act, 2005"],
                helpful_resources=["Women Helpline: 1091", "NCW: 7827-170-170"]
            ),
            LegalTopic(
                name="संपत्ति में अधिकार",
                description="पैतृक संपत्ति में महिलाओं के अधिकार",
                category="property_rights",
                language="hi",
                content="हिंदू उत्तराधिकार अधिनियम के अनुसार बेटियों का भी...",
                related_laws=["Hindu Succession Act, 1956 (Amended 2005)"],
                helpful_resources=["Legal Aid: 15100"]
            ),
        ]
        
        for topic in topics:
            db.add(topic)
        
        await db.commit()
        print(f"Created {len(topics)} legal topics")


async def main():
    """Main initialization function"""
    print("Initializing Sakti-Link database...")
    
    # Initialize database
    await init_db()
    print("Database tables created")
    
    # Create sample data
    await create_sample_learning_modules()
    await create_sample_skills()
    await create_sample_gigs()
    await create_sample_legal_topics()
    
    print("\nDatabase initialization complete!")
    print("Sample data created successfully.")


if __name__ == "__main__":
    asyncio.run(main())
