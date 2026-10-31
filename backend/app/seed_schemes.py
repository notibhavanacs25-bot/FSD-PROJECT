

from app.database import (
    connect_to_mongodb,
    close_mongodb_connection,
    get_database,
)

DEMO_SCHEMES = [
    {
        "schemeId": "DEMO-KA-001",
        "code": "DEMO-KA-001",
        "name": "Demo Student Support Scheme",
        "description": "Illustrative record for testing scheme search and eligibility APIs.",
        "state": "Karnataka",
        "benefits": ["Demo benefit for development only"],
        "eligibility": {
            "state": "Karnataka",
            "student": True,
            "max_annual_income": 250000,
        },
        "official_url": None,
        "source_verified_at": None,
        "disclaimer": "DEMO DATA ONLY. Replace with verified official information.",
    },
    {
        "schemeId": "DEMO-KA-002",
        "code": "DEMO-KA-002",
        "name": "Demo Farmer Support Scheme",
        "description": "Illustrative record for testing scheme search and eligibility APIs.",
        "state": "Karnataka",
        "benefits": ["Demo benefit for development only"],
        "eligibility": {
            "state": "Karnataka",
            "farmer": True,
        },
        "official_url": None,
        "source_verified_at": None,
        "disclaimer": "DEMO DATA ONLY. Replace with verified official information.",
    },
]


def main():
    connect_to_mongodb()

    try:
        db = get_database()
        print("MongoDB server:", db.client.address)

        schemes_collection = db["schemes"]

        for item in DEMO_SCHEMES:
            schemes_collection.update_one(
                {"schemeId": item["schemeId"]},
                {"$set": item},
                upsert=True,
            )

        print(f"Processed {len(DEMO_SCHEMES)} demo schemes.")
        print(f"Database name: {db.name}")
        print(f"Collection name: {schemes_collection.name}")
        print(
            "Total documents:",
            schemes_collection.count_documents({}),
        )

        for item in DEMO_SCHEMES:
            exists = schemes_collection.find_one(
                {"schemeId": item["schemeId"]},
                {"_id": 0, "schemeId": 1, "name": 1},
            )
            print(f"Verified {item['schemeId']}: {exists is not None}")

    finally:
        close_mongodb_connection()


if __name__ == "__main__":
    main()
