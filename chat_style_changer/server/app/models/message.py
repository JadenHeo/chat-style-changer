from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    chatroom_id: int
    timestamp: datetime
    sender: Optional[str] = None
    content: str    
    