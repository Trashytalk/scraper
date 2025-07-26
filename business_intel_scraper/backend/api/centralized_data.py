"""
Centralized Data Management API
Provides endpoints for data aggregation, analytics, and centralized storage
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json
import logging
import re
from pydantic import BaseModel

from ..db import get_db
from ..db.centralized_data import (
    CentralizedDataRecord,
    DataAnalytics,
    DataDeduplication,
)

# Auth dependency - optional for now
def get_current_user():
    """Placeholder auth function."""
    return {"user_id": "anonymous"}

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/data", tags=["centralized-data"])


def process_scraped_data(raw_data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
    """
    Process and clean raw scraped data.
    
    Args:
        raw_data: The original scraped data
        data_type: Type of data (news, ecommerce, social_media, etc.)
    
    Returns:
        Processed and cleaned data
    """
    processed = raw_data.copy()
    
    # Common processing for all data types
    if "text" in processed:
        # Clean and normalize text content
        text = processed["text"]
        if isinstance(text, str):
            # Remove excessive whitespace
            processed["text"] = " ".join(text.split())
            # Count words
            processed["word_count"] = len(text.split())
    
    # Extract and count links
    if "links" in processed:
        links = processed["links"]
        if isinstance(links, list):
            processed["link_count"] = len(links)
            # Clean and validate URLs
            valid_links = []
            for link in links:
                if isinstance(link, str) and (link.startswith("http") or link.startswith("/")):
                    valid_links.append(link)
            processed["links"] = valid_links
    
    # Extract and count images
    if "images" in processed:
        images = processed["images"]
        if isinstance(images, list):
            processed["image_count"] = len(images)
    
    # Data type specific processing
    if data_type == "news":
        processed = _process_news_data(processed)
    elif data_type == "ecommerce":
        processed = _process_ecommerce_data(processed)
    elif data_type == "social_media":
        processed = _process_social_media_data(processed)
    
    # Add processing metadata
    processed["_processing"] = {
        "processed_at": datetime.utcnow().isoformat(),
        "processor_version": "1.0",
        "data_type": data_type
    }
    
    return processed


def _process_news_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process news-specific data."""
    # Extract article metadata
    if "title" in data and isinstance(data["title"], str):
        data["title_word_count"] = len(data["title"].split())
    
    # Normalize publish date
    if "publish_date" in data:
        try:
            if isinstance(data["publish_date"], str):
                # Try to parse and normalize date format
                from dateutil import parser
                parsed_date = parser.parse(data["publish_date"])
                data["publish_date_normalized"] = parsed_date.isoformat()
        except:
            pass
    
    # Extract author information
    if "author" in data and isinstance(data["author"], str):
        data["has_author"] = True
        data["author_cleaned"] = data["author"].strip()
    else:
        data["has_author"] = False
    
    return data


def _process_ecommerce_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process e-commerce specific data."""
    import re
    
    # Normalize price information
    if "price" in data:
        price_str = str(data["price"])
        # Extract numeric price value
        price_match = re.search(r'[\d.,]+', price_str)
        if price_match:
            try:
                price_value = float(price_match.group().replace(',', ''))
                data["price_numeric"] = price_value
            except ValueError:
                pass
    
    # Process rating information
    if "rating" in data:
        rating_str = str(data["rating"])
        rating_match = re.search(r'[\d.]+', rating_str)
        if rating_match:
            try:
                rating_value = float(rating_match.group())
                data["rating_numeric"] = rating_value
            except ValueError:
                pass
    
    # Availability status
    if "availability" in data:
        availability = str(data["availability"]).lower()
        data["in_stock"] = "stock" in availability and "out" not in availability
    
    return data


def _process_social_media_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process social media specific data."""
    # Extract engagement metrics
    for metric in ["likes", "shares", "comments", "retweets"]:
        if metric in data:
            try:
                data[f"{metric}_numeric"] = int(str(data[metric]).replace(',', ''))
            except ValueError:
                pass
    
    # Process hashtags
    if "text" in data and isinstance(data["text"], str):
        import re
        hashtags = re.findall(r'#\w+', data["text"])
        data["hashtags"] = hashtags
        data["hashtag_count"] = len(hashtags)
    
    return data


class CentralizeDataRequest(BaseModel):
    job_id: int
    job_name: str
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class AnalyticsResponse(BaseModel):
    total_records: int
    total_jobs: int
    unique_sources: int
    data_types: Dict[str, int]
    quality_metrics: Dict[str, float]
    time_series: List[Dict[str, Any]]


def calculate_content_hash(data: Dict[str, Any]) -> str:
    """Calculate a hash for content deduplication"""
    # Create a normalized string representation
    content_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(content_str.encode()).hexdigest()


def calculate_data_quality(data: Dict[str, Any]) -> tuple[int, int]:
    """Calculate data quality and completeness scores"""
    total_fields = len(data)
    non_empty_fields = sum(1 for v in data.values() if v and str(v).strip())

    completeness = (
        int((non_empty_fields / total_fields) * 100) if total_fields > 0 else 0
    )

    # Quality score based on various factors
    quality_score = completeness

    # Bonus points for rich content
    if any(isinstance(v, str) and len(v) > 100 for v in data.values()):
        quality_score = min(100, quality_score + 10)

    # Bonus for URLs
    if any(
        "url" in str(k).lower() and str(v).startswith("http") for k, v in data.items()
    ):
        quality_score = min(100, quality_score + 5)

    return quality_score, completeness


def extract_metrics(data: Dict[str, Any]) -> tuple[int, int, int]:
    """Extract word count, link count, and image count from data"""
    word_count = 0
    link_count = 0
    image_count = 0

    for key, value in data.items():
        if isinstance(value, str):
            word_count += len(value.split())

            # Count links
            if "url" in key.lower() or "link" in key.lower():
                link_count += 1

            # Count image references
            if any(
                ext in value.lower()
                for ext in [".jpg", ".png", ".gif", ".jpeg", ".webp"]
            ):
                image_count += 1

    return word_count, link_count, image_count


@router.post("/centralize")
async def centralize_data(
    request: CentralizeDataRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Centralize data from a completed job into the unified database
    """
    try:
        centralized_count = 0
        duplicate_count = 0

        for item in request.data:
            # Calculate content hash for deduplication
            content_hash = calculate_content_hash(item)

            # Check for existing record with same hash
            existing = (
                db.query(CentralizedDataRecord)
                .filter(CentralizedDataRecord.content_hash == content_hash)
                .first()
            )

            if existing:
                duplicate_count += 1
                # Update duplicate tracking
                existing_dedup = (
                    db.query(DataDeduplication)
                    .filter(DataDeduplication.content_hash == content_hash)
                    .first()
                )

                if existing_dedup:
                    if existing_dedup.duplicate_record_ids:
                        existing_dedup.duplicate_record_ids.append(request.job_id)
                    else:
                        existing_dedup.duplicate_record_ids = [request.job_id]
                else:
                    new_dedup = DataDeduplication(
                        content_hash=content_hash,
                        canonical_record_id=existing.id,
                        duplicate_record_ids=[request.job_id],
                        similarity_score=100,
                        dedup_method="content_hash",
                    )
                    db.add(new_dedup)
                continue

            # Calculate quality metrics
            quality_score, completeness_score = calculate_data_quality(item)
            word_count, link_count, image_count = extract_metrics(item)

            # Determine data type
            data_type = "general"
            if "product" in str(item).lower() or "price" in str(item).lower():
                data_type = "ecommerce"
            elif "article" in str(item).lower() or "news" in str(item).lower():
                data_type = "news"
            elif "post" in str(item).lower() or "tweet" in str(item).lower():
                data_type = "social_media"

            # Create centralized record
            record = CentralizedDataRecord(
                source_job_id=request.job_id,
                source_job_name=request.job_name,
                source_job_type=request.metadata.get("job_type", "unknown"),
                source_url=item.get("url", ""),
                raw_data=item,
                processed_data=process_scraped_data(item, data_type),
                data_type=data_type,
                content_hash=content_hash,
                scraped_at=datetime.fromisoformat(
                    request.metadata.get(
                        "completed_at", datetime.utcnow().isoformat()
                    ).replace("Z", "+00:00")
                ),
                data_quality_score=quality_score,
                completeness_score=completeness_score,
                validation_status="valid" if quality_score >= 70 else "pending",
                word_count=word_count,
                link_count=link_count,
                image_count=image_count,
            )

            db.add(record)
            centralized_count += 1

        db.commit()

        # Schedule analytics update in background
        background_tasks.add_task(update_analytics, db)

        return {
            "status": "success",
            "centralized_records": centralized_count,
            "duplicates_found": duplicate_count,
            "total_processed": len(request.data),
        }

    except Exception as e:
        logger.error(f"Error centralizing data: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to centralize data: {str(e)}"
        )


@router.post("/consolidate")
async def consolidate_all_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Consolidate all job data into centralized database
    """
    try:
        # This would typically fetch all job results and centralize them
        # For now, return a success message
        background_tasks.add_task(update_analytics, db)

        return {
            "status": "success",
            "message": "Data consolidation initiated. This will run in the background.",
        }

    except Exception as e:
        logger.error(f"Error consolidating data: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to consolidate data: {str(e)}"
        )


@router.get("/analytics/summary")
async def get_analytics_summary(
    days: Optional[int] = 30,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> AnalyticsResponse:
    """
    Get comprehensive analytics from centralized data
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Query centralized data
        records = (
            db.query(CentralizedDataRecord)
            .filter(CentralizedDataRecord.centralized_at >= start_date)
            .all()
        )

        if not records:
            return AnalyticsResponse(
                total_records=0,
                total_jobs=0,
                unique_sources=0,
                data_types={},
                quality_metrics={},
                time_series=[],
            )

        # Calculate metrics
        total_records = len(records)
        unique_jobs = len(set(r.source_job_id for r in records))
        unique_sources = len(set(r.source_url for r in records if r.source_url))

        # Data type breakdown
        data_types = {}
        quality_scores = []
        completeness_scores = []

        for record in records:
            data_type = record.data_type or "unknown"
            data_types[data_type] = data_types.get(data_type, 0) + 1

            if record.data_quality_score:
                quality_scores.append(record.data_quality_score)
            if record.completeness_score:
                completeness_scores.append(record.completeness_score)

        # Quality metrics
        quality_metrics = {
            "avg_quality_score": (
                sum(quality_scores) / len(quality_scores) if quality_scores else 0
            ),
            "avg_completeness": (
                sum(completeness_scores) / len(completeness_scores)
                if completeness_scores
                else 0
            ),
            "high_quality_records": len([s for s in quality_scores if s >= 80]),
            "low_quality_records": len([s for s in quality_scores if s < 50]),
        }

        # Time series data (daily aggregation)
        time_series = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            day_records = [
                r for r in records if r.centralized_at.date() == current_date
            ]
            time_series.append(
                {
                    "date": current_date.isoformat(),
                    "records": len(day_records),
                    "jobs": len(set(r.source_job_id for r in day_records)),
                    "avg_quality": (
                        sum(
                            r.data_quality_score
                            for r in day_records
                            if r.data_quality_score
                        )
                        / len(day_records)
                        if day_records
                        else 0
                    ),
                }
            )
            current_date += timedelta(days=1)

        return AnalyticsResponse(
            total_records=total_records,
            total_jobs=unique_jobs,
            unique_sources=unique_sources,
            data_types=data_types,
            quality_metrics=quality_metrics,
            time_series=time_series,
        )

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/export/all")
async def export_all_data(
    format: str = "json",
    days: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Export all centralized data
    """
    try:
        query = db.query(CentralizedDataRecord)

        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(CentralizedDataRecord.centralized_at >= start_date)

        records = query.all()

        # Convert to export format
        export_data = []
        for record in records:
            export_item = {
                "record_id": record.record_uuid,
                "source_job": {
                    "id": record.source_job_id,
                    "name": record.source_job_name,
                    "type": record.source_job_type,
                },
                "data": record.raw_data,
                "metadata": {
                    "data_type": record.data_type,
                    "quality_score": record.data_quality_score,
                    "completeness_score": record.completeness_score,
                    "word_count": record.word_count,
                    "link_count": record.link_count,
                    "image_count": record.image_count,
                    "scraped_at": (
                        record.scraped_at.isoformat() if record.scraped_at else None
                    ),
                    "centralized_at": record.centralized_at.isoformat(),
                },
            }
            export_data.append(export_item)

        return {
            "status": "success",
            "export_date": datetime.utcnow().isoformat(),
            "total_records": len(export_data),
            "data": export_data,
        }

    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")


@router.post("/analytics/refresh")
async def refresh_analytics(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Refresh analytics calculations
    """
    try:
        background_tasks.add_task(update_analytics, db)
        return {"status": "success", "message": "Analytics refresh initiated"}

    except Exception as e:
        logger.error(f"Error refreshing analytics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to refresh analytics: {str(e)}"
        )


async def update_analytics(db: Session):
    """
    Background task to update analytics
    """
    try:
        # Calculate daily analytics
        today = datetime.utcnow().date()

        # Check if analytics already exist for today
        existing = (
            db.query(DataAnalytics)
            .filter(DataAnalytics.date == today, DataAnalytics.period_type == "daily")
            .first()
        )

        # Get today's records
        today_records = (
            db.query(CentralizedDataRecord)
            .filter(
                CentralizedDataRecord.centralized_at
                >= datetime.combine(today, datetime.min.time())
            )
            .all()
        )

        # Calculate metrics
        total_records = len(today_records)
        unique_jobs = len(set(r.source_job_id for r in today_records))
        unique_sources = len(set(r.source_url for r in today_records if r.source_url))

        # Count by data type
        news_count = len([r for r in today_records if r.data_type == "news"])
        ecommerce_count = len([r for r in today_records if r.data_type == "ecommerce"])
        social_count = len([r for r in today_records if r.data_type == "social_media"])
        other_count = total_records - news_count - ecommerce_count - social_count

        # Quality metrics
        quality_scores = [
            r.data_quality_score for r in today_records if r.data_quality_score
        ]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        if existing:
            # Update existing record
            existing.total_records = total_records
            existing.total_jobs = unique_jobs
            existing.unique_sources = unique_sources
            existing.news_records = news_count
            existing.ecommerce_records = ecommerce_count
            existing.social_media_records = social_count
            existing.other_records = other_count
            existing.avg_quality_score = int(avg_quality)
            existing.updated_at = datetime.utcnow()
        else:
            # Create new record
            analytics = DataAnalytics(
                date=today,
                period_type="daily",
                total_records=total_records,
                total_jobs=unique_jobs,
                unique_sources=unique_sources,
                news_records=news_count,
                ecommerce_records=ecommerce_count,
                social_media_records=social_count,
                other_records=other_count,
                avg_quality_score=int(avg_quality),
            )
            db.add(analytics)

        db.commit()
        logger.info(f"Analytics updated for {today}")

    except Exception as e:
        logger.error(f"Error updating analytics: {e}")
        db.rollback()
