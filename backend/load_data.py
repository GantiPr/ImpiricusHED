import csv
from datetime import datetime
from app.database import init_db, SessionLocal, Physician, Message

def load_physicians():
    """Load physicians from CSV into database"""
    db = SessionLocal()
    
    # Clear existing data
    db.query(Physician).delete()
    db.commit()
    
    with open('data/physicians.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            physician = Physician(
                physician_id=int(row['physician_id']),
                npi=row['npi'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                specialty=row['specialty'],
                state=row['state'],
                consent_opt_in=row['consent_opt_in'] == 'True',
                preferred_channel=row['preferred_channel']
            )
            db.add(physician)
    
    db.commit()
    db.close()
    print("✓ Loaded physicians")


def load_messages():
    """Load messages from CSV into database"""
    db = SessionLocal()
    
    # Clear existing data
    db.query(Message).delete()
    db.commit()
    
    with open('data/messages.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            message = Message(
                message_id=int(row['message_id']),
                physician_id=int(row['physician_id']),
                channel=row['channel'],
                direction=row['direction'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                message_text=row['message_text'],
                campaign_id=row['campaign_id'],
                topic=row['topic'],
                compliance_tag=row['compliance_tag'],
                sentiment=row['sentiment'],
                delivery_status=row['delivery_status'],
                response_latency_sec=float(row['response_latency_sec']) if row['response_latency_sec'] else None
            )
            db.add(message)
    
    db.commit()
    db.close()
    print("✓ Loaded messages")


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("✓ Database initialized")
    
    print("Loading data...")
    load_physicians()
    load_messages()
    print("\n✓ All data loaded successfully!")
