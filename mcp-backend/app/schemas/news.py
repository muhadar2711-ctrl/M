from pydantic import BaseModel, ConfigDict
from typing import List

class NewsEventItem(BaseModel):
    impact: str
    currency: str
    event: str
    time: str
    source: str

    model_config = ConfigDict(from_attributes=True)

class NewsAPIResponse(BaseModel):
    status: str
    count: int
    data: List[NewsEventItem]

    model_config = ConfigDict(from_attributes=True)
