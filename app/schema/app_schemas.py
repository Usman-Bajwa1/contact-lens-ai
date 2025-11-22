from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ContactBase(BaseModel):
    full_name: str = Field(..., description="Full name on the card")
    job_title: Optional[str] = Field(None, description="Job title or role")
    company: Optional[str] = Field(None, description="Company name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number formatted internationally")
    address: Optional[str] = Field(None, description="Physical address")
    tags: List[str] = Field(default_factory=list, description="Inferred industry tags (e.g. 'Tech', 'Medical')")
    
    skills: List[str] = Field(default_factory=list, description="Inferred professional skills based on job title/company")
    social_media: Dict[str, str] = Field(default_factory=dict, description="Inferred potential social handles (e.g. {'linkedin': '...', 'twitter': '...'}")

class ContactCreate(ContactBase):
    confidence_score: float = Field(..., description="Confidence score (0.0-1.0) based on text clarity")
    summary: Optional[str] = Field(None, description="Short AI generated summary of the person")

class ContactResponse(ContactCreate):
    id: str
    is_duplicate: bool = False
    duplicate_reason: Optional[str] = None 

class DuplicateCheckResult(BaseModel):
    is_duplicate: bool = Field(..., description="True if the person already exists in the list")
    matched_id: Optional[str] = Field(None, description="The ID of the existing contact that matches")
    reason: str = Field(..., description="Explanation of why it is a duplicate (e.g. 'Same email', 'Phonetic name match')")