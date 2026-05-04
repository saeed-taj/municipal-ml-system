from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# What the user sends us
class ComplaintCreate(BaseModel):
    issue_description: str
    reporter_name: Optional[str] = "Anonymous"
    location: Optional[str] = "Anonymous"
    email: Optional[str] = "Anonymous"
    issue_type : Optional[str] = "Anonymous"

# What we send back to the user (includes ML results)
class ComplaintResponse(BaseModel):
    id: int
    issue_description: str
    category: str
    priority: str
    status: str
    created_at: datetime