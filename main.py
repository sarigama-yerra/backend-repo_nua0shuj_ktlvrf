import os
from fastapi import FastAPI, HTTPException
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
