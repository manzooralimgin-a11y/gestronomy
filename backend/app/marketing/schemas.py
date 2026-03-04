from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    platform: str
    rating: float | None = None
    text: str | None = None
    sentiment_score: float | None = None
    ai_response: str | None = None
    response_status: str
    author_name: str | None = None
    review_date: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ReviewResponseRequest(BaseModel):
    review_id: int
    response: str | None = None


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    target_segment: str | None = None
    content: str | None = None
    status: str
    sent_count: int
    open_rate: float | None = None
    conversion_rate: float | None = None
    scheduled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CampaignCreate(BaseModel):
    name: str
    type: str
    target_segment: str | None = None
    content: str | None = None
    status: str = "draft"
    scheduled_at: datetime | None = None


class SocialPostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    platform: str
    content: str | None = None
    media_urls: dict | None = None
    status: str
    engagement_json: dict | None = None
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class SocialPostCreate(BaseModel):
    platform: str
    content: str | None = None
    media_urls: dict | None = None
    status: str = "draft"
    scheduled_at: datetime | None = None
