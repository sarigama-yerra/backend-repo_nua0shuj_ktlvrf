"""
Database Schemas for Real Estate App

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase class name.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal

class Property(BaseModel):
    title: str = Field(..., description="Property title")
    description: Optional[str] = Field(None, description="Short description")
    category: Literal["residential", "commercial", "industrial", "land"] = Field(..., description="Property category")
    price: Optional[float] = Field(None, ge=0, description="Listing price")
    location: str = Field(..., description="City/Area")
    images: List[HttpUrl] = Field(default_factory=list, description="Image URLs")
    amenities: List[str] = Field(default_factory=list, description="Key amenities")
    featured: bool = Field(default=False, description="Show on homepage carousel")

class Review(BaseModel):
    name: str = Field(..., description="Reviewer name")
    rating: int = Field(..., ge=1, le=5, description="Rating out of 5")
    comment: str = Field(..., description="Review text")

class Inquiry(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    message: str = Field(..., description="User message or query")
    interest_category: Optional[Literal["residential", "commercial", "industrial", "land"]] = None
