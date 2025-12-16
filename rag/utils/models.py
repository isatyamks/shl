from typing import List, Optional
from pydantic import BaseModel, Field

class UserIntent(BaseModel):
    categories: List[str] = Field(description="List of categories from: tech, sales, admin, leadership, marketing, general, finance, hr, operations")
    explicit_keywords: List[str] = Field(description="Specific hard skills (e.g. Java, Excel, Accounting) or soft skills found in the query")
    behavioral: bool = Field(description="True if the user asks for soft skills, collaboration, personality, or culture fit")
    duration_max: Optional[int] = Field(description="Maximum duration in minutes. Convert hours to minutes (e.g. 1 hour = 60).")
    is_entry_level: bool = Field(description="True if query mentions graduate, fresher, entry level, or 0-2 years")
