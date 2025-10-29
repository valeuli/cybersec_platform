from pydantic import BaseModel, UUID4
from datetime import datetime

class ProgressTrack(BaseModel):
    module_id: UUID4
    viewed: bool = True

class ProgressOut(BaseModel):
    user_id: UUID4
    lesson_id: UUID4
    last_accessed_at: datetime
    message: str