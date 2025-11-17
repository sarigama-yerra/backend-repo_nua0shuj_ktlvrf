import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Property, Review, Inquiry

app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers

def serialize_doc(doc: dict):
    if not doc:
        return doc
    doc["id"] = str(doc.get("_id"))
    doc.pop("_id", None)
    return doc

# Health
@app.get("/")
def read_root():
    return {"message": "Real Estate API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Seed logic
@app.post("/admin/seed")
def seed_database(reset: bool = Query(default=False, description="Drop collections before seeding")):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    # Optionally reset collections
    if reset:
        db.drop_collection("property")
        db.drop_collection("review")
        db.drop_collection("inquiry")

    prop_count = db["property"].count_documents({})
    rev_count = db["review"].count_documents({})

    seeded_props = 0
    seeded_reviews = 0

    if prop_count == 0:
        sample_props = [
            {
                "title": "Casagrand Aurelia - Luxury Residences",
                "description": "Spacious 3 & 4 BHK homes with skyline views and premium amenities.",
                "category": "residential",
                "price": 18500000,
                "location": "Chennai - OMR",
                "images": [
                    "https://images.unsplash.com/photo-1505691938895-1758d7feb511?q=80&w=1600&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1515263487990-61b07816b324?q=80&w=1600&auto=format&fit=crop"
                ],
                "amenities": ["Infinity Pool", "Clubhouse", "Gym", "Landscaped Gardens"],
                "featured": True,
            },
            {
                "title": "Casagrand Meridian - Grade A Offices",
                "description": "Flexible commercial spaces with smart access and ample parking.",
                "category": "commercial",
                "price": 42000000,
                "location": "Bengaluru - ORR",
                "images": [
                    "https://images.unsplash.com/photo-1460317442991-0ec209397118?q=80&w=1600&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1433840496881-cbd845929862?q=80&w=1600&auto=format&fit=crop"
                ],
                "amenities": ["Smart Access", "Food Court", "EV Charging", "High-speed Elevators"],
                "featured": True,
            },
            {
                "title": "Casagrand Vertex - Industrial Park",
                "description": "Built-to-suit facilities with excellent connectivity and utilities.",
                "category": "industrial",
                "price": 98000000,
                "location": "Chennai - Sriperumbudur",
                "images": [
                    "https://images.unsplash.com/photo-1587654780291-39c9404d746b?q=80&w=1600&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1578579933455-1f35d87dfbaf?q=80&w=1600&auto=format&fit=crop"
                ],
                "amenities": ["24x7 Security", "Truck Docks", "Power Backup", "Warehouse Automation"],
                "featured": False,
            },
            {
                "title": "Casagrand Terra - Premium Plots",
                "description": "Gated community plots with parks, wide roads, and ready infrastructure.",
                "category": "land",
                "price": 7500000,
                "location": "Coimbatore - Saravanampatti",
                "images": [
                    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1600&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1471623320832-752e8bbf8413?q=80&w=1600&auto=format&fit=crop"
                ],
                "amenities": ["Gated Entry", "Parks", "Street Lighting", "Water & Sewage"],
                "featured": True,
            },
            {
                "title": "Casagrand Promenade - Sky Villas",
                "description": "Limited edition sky villas with private decks and concierge services.",
                "category": "residential",
                "price": 32500000,
                "location": "Chennai - ECR",
                "images": [
                    "https://images.unsplash.com/photo-1499955085172-a104c9463ece?q=80&w=1600&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?q=80&w=1600&auto=format&fit=crop"
                ],
                "amenities": ["Concierge", "Sky Lounge", "Spa", "Banquet"],
                "featured": False,
            },
        ]
        for p in sample_props:
            create_document("property", p)
            seeded_props += 1

    if rev_count == 0:
        sample_reviews = [
            {"name": "Anita R.", "rating": 5, "comment": "Seamless booking process and excellent site team. Highly recommend!"},
            {"name": "Vikram S.", "rating": 4, "comment": "Great locations and thoughtful amenities. Overall a solid experience."},
            {"name": "Leena K.", "rating": 5, "comment": "Loved the finish quality and community spaces at Casagrand Aurelia."},
        ]
        for r in sample_reviews:
            create_document("review", r)
            seeded_reviews += 1

    return {
        "seeded": True,
        "reset": reset,
        "properties_before": prop_count,
        "reviews_before": rev_count,
        "properties_added": seeded_props,
        "reviews_added": seeded_reviews,
        "total_properties": db["property"].count_documents({}),
        "total_reviews": db["review"].count_documents({}),
    }

# Convenience GET seed for browser use
@app.get("/admin/seed")
def seed_database_get(reset: bool = Query(default=False, description="Drop collections before seeding")):
    return seed_database(reset=reset)

# Properties
@app.get("/api/properties", response_model=List[dict])
def list_properties(category: str | None = None, featured: bool | None = None):
    filter_q = {}
    if category:
        filter_q["category"] = category
    if featured is not None:
        filter_q["featured"] = featured
    docs = get_documents("property", filter_q)
    return [serialize_doc(d) for d in docs]

@app.post("/api/properties", status_code=201)
def create_property(prop: Property):
    new_id = create_document("property", prop)
    return {"id": new_id}

# Reviews
@app.get("/api/reviews", response_model=List[dict])
def list_reviews(limit: int = 20):
    docs = get_documents("review", {}, limit)
    return [serialize_doc(d) for d in docs]

@app.post("/api/reviews", status_code=201)
def create_review(review: Review):
    new_id = create_document("review", review)
    return {"id": new_id}

# Inquiries
@app.post("/api/inquiries", status_code=201)
def create_inquiry(inquiry: Inquiry):
    new_id = create_document("inquiry", inquiry)
    return {"id": new_id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
