"""
WareXpert - Main Application Entry Point
Flask application factory and server startup
"""

import os
from dotenv import load_dotenv
from app import create_app, db

# Load environment variables from .env file
load_dotenv()

# Get environment from ENV variable or default to development
env = os.getenv('FLASK_ENV', 'development')

# Create Flask application instance
app = create_app(env)

@app.cli.command()
def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")

@app.cli.command()
def seed_db():
    """Seed the database with initial data for development"""
    from app.models import Tenant, User, Warehouse, Location, Product
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        # Check if data already exists
        if Tenant.query.first():
            print("⚠️  Database already seeded. Skipping...")
            return
        
        # Create demo tenant
        tenant = Tenant(
            name="Demo Corp",
            subdomain="demo",
            plan="premium"
        )
        db.session.add(tenant)
        db.session.flush()
        
        # Create admin user
        admin = User(
            tenant_id=tenant.id,
            email="admin@demo.com",
            password_hash=generate_password_hash("admin123"),
            full_name="Admin Usuario",
            role="ADMIN",
            is_active=True
        )
        db.session.add(admin)
        
        # Create seller user
        seller = User(
            tenant_id=tenant.id,
            email="seller@demo.com",
            password_hash=generate_password_hash("seller123"),
            full_name="Vendedor Demo",
            role="SELLER",
            is_active=True
        )
        db.session.add(seller)
        
        # Create warehouse
        warehouse = Warehouse(
            tenant_id=tenant.id,
            code="WH-001",
            name="Bodega Principal",
            length=50.0,
            width=30.0,
            height=6.0,
            total_capacity_m3=9000.0,
            total_capacity_kg=500000.0
        )
        db.session.add(warehouse)
        db.session.flush()
        
        # Create sample locations
        locations_data = [
            {"code": "A-01-01", "zone": "picking", "x": 2.0, "y": 2.0, "z": 0.0},
            {"code": "A-01-02", "zone": "picking", "x": 2.0, "y": 4.0, "z": 0.0},
            {"code": "A-02-01", "zone": "picking", "x": 4.0, "y": 2.0, "z": 0.0},
            {"code": "B-01-01", "zone": "storage", "x": 10.0, "y": 2.0, "z": 0.0},
            {"code": "B-01-02", "zone": "storage", "x": 10.0, "y": 4.0, "z": 0.0},
        ]
        
        for loc_data in locations_data:
            location = Location(
                warehouse_id=warehouse.id,
                code=loc_data["code"],
                type="shelf",
                zone=loc_data["zone"],
                x_position=loc_data["x"],
                y_position=loc_data["y"],
                z_position=loc_data["z"],
                length=1.2,
                width=0.6,
                height=2.0,
                capacity_m3=1.44,
                capacity_kg=500.0,
                max_stackable=10
            )
            db.session.add(location)
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database seeded successfully!")
        print(f"   - Tenant: {tenant.name}")
        print(f"   - Admin user: admin@demo.com / admin123")
        print(f"   - Seller user: seller@demo.com / seller123")
        print(f"   - Warehouse: {warehouse.name}")
        print(f"   - Locations: {len(locations_data)} created")

if __name__ == '__main__':
    # Run development server
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
