"""Reset migration state and apply fresh migrations"""
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres.yskedmzigaglodsnjqoh:peBshgusTH9sVTkM@aws-1-us-east-2.pooler.supabase.com:6543/postgres'

from app import create_app, db
from sqlalchemy import text

app = create_app('development')

with app.app_context():
    # Drop alembic_version table to reset migration state
    print("🔄 Resetting migration state...")
    try:
        db.session.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        db.session.commit()
        print("✅ Migration state reset")
    except Exception as e:
        print(f"⚠️  Error resetting: {e}")
        db.session.rollback()
    
    # Create all tables using SQLAlchemy
    print("\n🔄 Creating all tables...")
    try:
        db.create_all()
        print("✅ All tables created successfully!")
        
        # List created tables
        result = db.session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        print(f"\n📊 Tables in database ({len(tables)}):")
        for table in tables:
            print(f"   - {table}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        db.session.rollback()
