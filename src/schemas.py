from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Article(BaseModel):
    date: datetime
    title: str
    summary: str
    link: str
    text: Optional[str] = None
