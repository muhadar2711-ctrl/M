from pydantic import BaseModel, ConfigDict
from typing import Optional

class SentimentAnalysisResult(BaseModel):
    symbol: str
    sentiment: str
    confidence_score: int
    source: str

    model_config = ConfigDict(from_attributes=True)
