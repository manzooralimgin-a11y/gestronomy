from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.marketing.models import Campaign, Review, SocialPost
from app.marketing.schemas import CampaignCreate, ReviewResponseRequest, SocialPostCreate


async def get_reviews(
    db: AsyncSession, platform: str | None = None, limit: int = 100
) -> list[Review]:
    query = select(Review).order_by(Review.created_at.desc()).limit(limit)
    if platform:
        query = query.where(Review.platform == platform)
    result = await db.execute(query)
    return list(result.scalars().all())


async def respond_to_review(
    db: AsyncSession, review_id: int, payload: ReviewResponseRequest
) -> Review:
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    if payload.response:
        review.ai_response = payload.response
        review.response_status = "drafted"
    else:
        review.ai_response = "Stub: AI-generated response pending."
        review.response_status = "drafted"
    await db.flush()
    await db.refresh(review)
    return review


async def get_campaigns(
    db: AsyncSession, status_filter: str | None = None, limit: int = 100
) -> list[Campaign]:
    query = select(Campaign).order_by(Campaign.created_at.desc()).limit(limit)
    if status_filter:
        query = query.where(Campaign.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_campaign(db: AsyncSession, payload: CampaignCreate) -> Campaign:
    campaign = Campaign(**payload.model_dump())
    db.add(campaign)
    await db.flush()
    await db.refresh(campaign)
    return campaign


async def get_social_posts(
    db: AsyncSession, platform: str | None = None, limit: int = 100
) -> list[SocialPost]:
    query = select(SocialPost).order_by(SocialPost.created_at.desc()).limit(limit)
    if platform:
        query = query.where(SocialPost.platform == platform)
    result = await db.execute(query)
    return list(result.scalars().all())


async def generate_social_content(
    db: AsyncSession, payload: SocialPostCreate
) -> SocialPost:
    post = SocialPost(
        platform=payload.platform,
        content=payload.content or "Stub: AI-generated content pending.",
        media_urls=payload.media_urls,
        status="draft",
        scheduled_at=payload.scheduled_at,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


async def get_reputation_score(db: AsyncSession) -> dict:
    result = await db.execute(
        select(
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("total_reviews"),
            func.avg(Review.sentiment_score).label("avg_sentiment"),
        )
    )
    row = result.one()
    return {
        "avg_rating": round(float(row.avg_rating), 2) if row.avg_rating else None,
        "total_reviews": row.total_reviews or 0,
        "avg_sentiment": round(float(row.avg_sentiment), 2) if row.avg_sentiment else None,
    }
