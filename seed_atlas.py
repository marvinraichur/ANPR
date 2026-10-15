#!/usr/bin/env python3
"""
Atlas Seed Script
=================
Seeds the MongoDB Atlas database with:
  - 17+ sample vehicles (with owner_phone for SMS alerts)
  - Pre-defined PUC certificate records
  - Pre-defined Fitness Certificate records

Run this once to populate Atlas:
    python seed_atlas.py

The script is idempotent — it upserts records so it's safe to re-run.
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Load .env first
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
    print("✅ .env loaded")
except ImportError:
    print("⚠️  python-dotenv not installed. Using existing environment variables.")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("seed_atlas")

# ── MongoDB Connection ──────────────────────────────────────────────────────

ATLAS_URI = os.getenv("MONGODB_ATLAS_URI", "")
DB_NAME   = os.getenv("DB_NAME", "anpr_database")

if not ATLAS_URI:
    print("❌ MONGODB_ATLAS_URI not set in .env. Cannot seed Atlas.")
    sys.exit(1)

try:
    from pymongo import MongoClient, UpdateOne
    from pymongo.errors import BulkWriteError
    client = MongoClient(ATLAS_URI, serverSelectionTimeoutMS=10000)
    db = client[DB_NAME]
    # Test connection
    client.admin.command("ping")
    print(f"✅ Connected to MongoDB Atlas — database: {DB_NAME}")
except Exception as e:
    print(f"❌ Cannot connect to MongoDB Atlas: {e}")
    sys.exit(1)

# ── Import seeded data ──────────────────────────────────────────────────────

from src.services.seeded_data import get_seeded_puc_data, get_seeded_fc_data

# ── Vehicle Records (with owner_phone for SMS alerts) ───────────────────────

VEHICLES = [
    # -- ELIGIBLE VEHICLES --
    {"registration_number": "KA01MJ2023", "registration_date": datetime(2023, 1, 15),  "fuel_type": "PETROL",   "owner_name": "Arjun Sharma",   "owner_phone": "9845012345", "vehicle_make": "Toyota",        "vehicle_model": "Corolla",      "state": "Karnataka"},
    {"registration_number": "MH02CD5678", "registration_date": datetime(2019, 6, 20),  "fuel_type": "PETROL",   "owner_name": "Priya Patel",    "owner_phone": "9820067891", "vehicle_make": "Maruti Suzuki", "vehicle_model": "Swift",        "state": "Maharashtra"},
    {"registration_number": "KA63MA6613", "registration_date": datetime(2020, 7, 4),   "fuel_type": "PETROL",   "owner_name": "Suresh Babu",    "owner_phone": "9876554321", "vehicle_make": "Hyundai",       "vehicle_model": "Creta",        "state": "Karnataka"},
    {"registration_number": "GJ01KL3456", "registration_date": datetime(2021, 9, 12),  "fuel_type": "PETROL",   "owner_name": "Nilesh Mehta",   "owner_phone": "9824011234", "vehicle_make": "Volkswagen",    "vehicle_model": "Polo",         "state": "Gujarat"},
    {"registration_number": "TN22AB4512", "registration_date": datetime(2022, 3, 8),   "fuel_type": "CNG",      "owner_name": "Kavitha Rajan",  "owner_phone": "9444012345", "vehicle_make": "Maruti Suzuki", "vehicle_model": "Wagon R CNG",  "state": "Tamil Nadu"},
    {"registration_number": "DL07KL9988", "registration_date": datetime(2022, 1, 1),   "fuel_type": "PETROL",   "owner_name": "Aman Verma",     "owner_phone": "9810056789", "vehicle_make": "Kia",           "vehicle_model": "Seltos",       "state": "Delhi"},
    {"registration_number": "MH12EV2024", "registration_date": datetime(2024, 2, 14),  "fuel_type": "ELECTRIC", "owner_name": "Sneha Kulkarni", "owner_phone": "9920078901", "vehicle_make": "Tata",          "vehicle_model": "Nexon EV",     "state": "Maharashtra"},
    {"registration_number": "AP31RS2345", "registration_date": datetime(2019, 7, 30),  "fuel_type": "PETROL",   "owner_name": "Lakshmi Devi",   "owner_phone": "9848056789", "vehicle_make": "Maruti Suzuki", "vehicle_model": "Baleno",       "state": "Andhra Pradesh"},
    # -- EXPIRING SOON PUC --
    {"registration_number": "TN09XY5678", "registration_date": datetime(2012, 3, 15),  "fuel_type": "PETROL",   "owner_name": "Ramesh Naidu",   "owner_phone": "9444023456", "vehicle_make": "Ford",          "vehicle_model": "EcoSport",     "state": "Tamil Nadu"},
    # -- DENIED - OVER AGE LIMIT --
    {"registration_number": "KA05EF2008", "registration_date": datetime(2008, 11, 10), "fuel_type": "PETROL",   "owner_name": "Mohan Rao",      "owner_phone": "9886012345", "vehicle_make": "Maruti Suzuki", "vehicle_model": "Alto 800",     "state": "Karnataka"},
    {"registration_number": "MH04XY2007", "registration_date": datetime(2007, 5, 17),  "fuel_type": "PETROL",   "owner_name": "Dilip Joshi",    "owner_phone": "9823045678", "vehicle_make": "Maruti Suzuki", "vehicle_model": "Zen Estilo",   "state": "Maharashtra"},
    {"registration_number": "UP16MN9012", "registration_date": datetime(2005, 11, 8),  "fuel_type": "DIESEL",   "owner_name": "Vikram Singh",   "owner_phone": "9415023456", "vehicle_make": "Mahindra",      "vehicle_model": "Scorpio",      "state": "Uttar Pradesh"},
    {"registration_number": "RJ14PQ7890", "registration_date": datetime(2003, 4, 25),  "fuel_type": "DIESEL",   "owner_name": "Bharat Verma",   "owner_phone": "9414034567", "vehicle_make": "Hyundai",       "vehicle_model": "Accent",       "state": "Rajasthan"},
    # -- DENIED - BUT HAVE VALID FC --
    {"registration_number": "DL05AB1234", "registration_date": datetime(2010, 6, 10),  "fuel_type": "DIESEL",   "owner_name": "Rajesh Khanna",  "owner_phone": "9811034567", "vehicle_make": "Honda",         "vehicle_model": "City",         "state": "Delhi"},
    {"registration_number": "DL09PQ2012", "registration_date": datetime(2012, 3, 25),  "fuel_type": "DIESEL",   "owner_name": "Sunita Batra",   "owner_phone": "9871056789", "vehicle_make": "Toyota",        "vehicle_model": "Innova",       "state": "Delhi"},
    # -- FC EXPIRED --
    {"registration_number": "KA05AB1234", "registration_date": datetime(2015, 8, 20),  "fuel_type": "DIESEL",   "owner_name": "Ravi Kumar",     "owner_phone": "9900045678", "vehicle_make": "Tata",          "vehicle_model": "Nexon Diesel", "state": "Karnataka"},
    # -- SCRAPPAGE (max FC used) --
    {"registration_number": "GJ05MK8523", "registration_date": datetime(2007, 2, 14),  "fuel_type": "DIESEL",   "owner_name": "Amit Shah",      "owner_phone": "9825056789", "vehicle_make": "Mahindra",      "vehicle_model": "Bolero",       "state": "Gujarat"},
]


def seed_vehicles():
    """Upsert all vehicles into the vehicles collection."""
    col = db["vehicles"]
    ops = []
    for v in VEHICLES:
        doc = dict(v)
        doc["registration_date"] = v["registration_date"].isoformat()
        doc["age_years"] = round((datetime.now() - v["registration_date"]).days / 365.25, 2)
        doc["updated_at"] = datetime.now().isoformat()
        ops.append(UpdateOne(
            {"registration_number": v["registration_number"]},
            {"$set": doc},
            upsert=True
        ))
    result = col.bulk_write(ops)
    print(f"✅ Vehicles  — upserted: {result.upserted_count}, modified: {result.modified_count}, total: {len(VEHICLES)}")


def seed_puc():
    """Upsert all PUC records into the puc_records collection."""
    col = db["puc_records"]
    seeded = get_seeded_puc_data()
    ops = []
    for reg, data in seeded.items():
        doc = dict(data)
        doc["updated_at"] = datetime.now().isoformat()
        ops.append(UpdateOne(
            {"registration_number": reg},
            {"$set": doc},
            upsert=True
        ))
    result = col.bulk_write(ops)
    print(f"✅ PUC data  — upserted: {result.upserted_count}, modified: {result.modified_count}, total: {len(seeded)}")


def seed_fitness_certs():
    """Upsert all FC records into the fitness_certificates collection."""
    col = db["fitness_certificates"]
    seeded = get_seeded_fc_data()
    ops = []
    for reg, fc_list in seeded.items():
        for fc in fc_list:
            doc = dict(fc)
            doc["updated_at"] = datetime.now().isoformat()
            ops.append(UpdateOne(
                {"certificate_number": fc["certificate_number"]},
                {"$set": doc},
                upsert=True
            ))
    result = col.bulk_write(ops)
    total = sum(len(v) for v in seeded.values())
    print(f"✅ FC data   — upserted: {result.upserted_count}, modified: {result.modified_count}, total: {total}")


if __name__ == "__main__":
    print("\n🌱 Seeding MongoDB Atlas...")
    print("=" * 50)
    seed_vehicles()
    seed_puc()
    seed_fitness_certs()
    print("=" * 50)
    print("🎉 Seeding complete!\n")
    client.close()
