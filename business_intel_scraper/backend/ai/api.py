"""
AI Integration API Endpoints
Provides REST API for AI-powered data processing and analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from . import AIProcessor


# Pydantic models for API
class TextProcessingRequest(BaseModel):
    text: str = Field(..., description="Text to process")
    include_entities: bool = Field(default=True, description="Extract entities")
    include_classification: bool = Field(default=True, description="Classify text")
    include_sentiment: bool = Field(default=True, description="Analyze sentiment")
    include_summary: bool = Field(default=True, description="Generate summary")


class DataProcessingRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Data items to process")
    detect_duplicates: bool = Field(default=True, description="Detect duplicates")
    calculate_quality: bool = Field(
        default=True, description="Calculate quality scores"
    )


class DuplicateDetectionRequest(BaseModel):
    texts: List[str] = Field(..., description="Texts to check for duplicates")
    threshold: Optional[float] = Field(default=0.85, description="Similarity threshold")


class EntityExtractionResponse(BaseModel):
    text: str
    label: str
    confidence: float
    start: int
    end: int
    metadata: Optional[Dict[str, Any]] = None


class ClassificationResponse(BaseModel):
    category: str
    confidence: float
    subcategories: Optional[List[Dict[str, float]]] = None


class ProcessedDataResponse(BaseModel):
    original_data: Dict[str, Any]
    entities: List[EntityExtractionResponse]
    classification: ClassificationResponse
    summary: Optional[str] = None
    sentiment: Optional[Dict[str, float]] = None
    duplicates: Optional[List[str]] = None
    quality_score: float


class AIStatusResponse(BaseModel):
    ai_enabled: bool
    models: Dict[str, bool]
    capabilities: Dict[str, bool]
    version: str = "1.0.0"


# Create router
router = APIRouter(prefix="/ai", tags=["ai"])

# Initialize AI processor
ai_processor = None


def get_ai_processor():
    global ai_processor
    if ai_processor is None:
        ai_processor = AIProcessor()
    return ai_processor


@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status():
    """Get AI system status and capabilities"""
    try:
        processor = get_ai_processor()
        status = processor.get_model_status()

        return AIStatusResponse(
            ai_enabled=status["ai_enabled"],
            models=status["models"],
            capabilities=status["capabilities"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get AI status: {str(e)}"
        )


@router.post("/process-text")
async def process_text(request: TextProcessingRequest):
    """Process text with AI analysis"""
    try:
        processor = get_ai_processor()
        result = {}

        if request.include_entities:
            entities = processor.extract_entities(request.text)
            result["entities"] = [
                EntityExtractionResponse(
                    text=e.text,
                    label=e.label,
                    confidence=e.confidence,
                    start=e.start,
                    end=e.end,
                    metadata=e.metadata,
                )
                for e in entities
            ]

        if request.include_classification:
            classification = processor.classify_text(request.text)
            result["classification"] = ClassificationResponse(
                category=classification.category, confidence=classification.confidence
            )

        if request.include_sentiment:
            sentiment = processor.analyze_sentiment(request.text)
            result["sentiment"] = sentiment

        if request.include_summary:
            summary = processor.summarize_text(request.text)
            result["summary"] = summary

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")


@router.post("/extract-entities", response_model=List[EntityExtractionResponse])
async def extract_entities(
    text: str = Query(..., description="Text to extract entities from")
):
    """Extract named entities from text"""
    try:
        processor = get_ai_processor()
        entities = processor.extract_entities(text)

        return [
            EntityExtractionResponse(
                text=e.text,
                label=e.label,
                confidence=e.confidence,
                start=e.start,
                end=e.end,
                metadata=e.metadata,
            )
            for e in entities
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Entity extraction failed: {str(e)}"
        )


@router.post("/classify-text", response_model=ClassificationResponse)
async def classify_text(text: str = Query(..., description="Text to classify")):
    """Classify text into categories"""
    try:
        processor = get_ai_processor()
        classification = processor.classify_text(text)

        return ClassificationResponse(
            category=classification.category, confidence=classification.confidence
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Text classification failed: {str(e)}"
        )


@router.post("/analyze-sentiment")
async def analyze_sentiment(text: str = Query(..., description="Text to analyze")):
    """Analyze sentiment of text"""
    try:
        processor = get_ai_processor()
        sentiment = processor.analyze_sentiment(text)

        return {"sentiment": sentiment}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Sentiment analysis failed: {str(e)}"
        )


@router.post("/summarize-text")
async def summarize_text(
    text: str = Query(..., description="Text to summarize"),
    max_length: int = Query(150, description="Maximum summary length"),
):
    """Generate text summary"""
    try:
        processor = get_ai_processor()
        summary = processor.summarize_text(text, max_length)

        return {"summary": summary}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Text summarization failed: {str(e)}"
        )


@router.post("/detect-duplicates")
async def detect_duplicates(request: DuplicateDetectionRequest):
    """Detect duplicate or near-duplicate texts"""
    try:
        processor = get_ai_processor()
        duplicates = processor.detect_duplicates(request.texts, request.threshold)

        return {
            "duplicate_groups": duplicates,
            "total_groups": len(duplicates),
            "total_duplicates": sum(len(group) for group in duplicates),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Duplicate detection failed: {str(e)}"
        )


@router.post("/process-data", response_model=List[ProcessedDataResponse])
async def process_data(request: DataProcessingRequest):
    """Process structured data with AI enhancements"""
    try:
        processor = get_ai_processor()
        processed_data = await processor.enhance_scraped_data(request.data)

        results = []
        for data in processed_data:
            result = ProcessedDataResponse(
                original_data=data.original_data,
                entities=[
                    EntityExtractionResponse(
                        text=e.text,
                        label=e.label,
                        confidence=e.confidence,
                        start=e.start,
                        end=e.end,
                        metadata=e.metadata,
                    )
                    for e in data.entities
                ],
                classification=ClassificationResponse(
                    category=data.classification.category,
                    confidence=data.classification.confidence,
                ),
                summary=data.summary,
                sentiment=data.sentiment,
                duplicates=data.duplicates,
                quality_score=data.quality_score,
            )
            results.append(result)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data processing failed: {str(e)}")


@router.post("/quality-score")
async def calculate_quality_score(data: Dict[str, Any]):
    """Calculate data quality score"""
    try:
        processor = get_ai_processor()
        score = processor.calculate_quality_score(data)

        return {
            "quality_score": score,
            "quality_grade": (
                "A"
                if score >= 0.9
                else "B" if score >= 0.7 else "C" if score >= 0.5 else "D"
            ),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality scoring failed: {str(e)}")


@router.get("/models")
async def list_models():
    """List available AI models and their status"""
    try:
        processor = get_ai_processor()
        status = processor.get_model_status()

        model_info = {
            "spacy": {
                "loaded": status["models"]["spacy"],
                "purpose": "Named Entity Recognition",
                "capabilities": ["entity_extraction"],
            },
            "transformers": {
                "loaded": status["models"]["transformers"],
                "purpose": "Text Classification and Sentiment",
                "capabilities": ["classification", "sentiment", "summarization"],
            },
            "sentence_transformers": {
                "loaded": status["models"]["sentence_transformers"],
                "purpose": "Text Embeddings",
                "capabilities": ["duplicate_detection", "similarity"],
            },
            "openai": {
                "loaded": status["models"]["openai"],
                "purpose": "Advanced Language Processing",
                "capabilities": ["advanced_classification", "creative_generation"],
            },
        }

        return model_info

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.post("/batch-process")
async def batch_process(
    background_tasks: BackgroundTasks,
    data: List[Dict[str, Any]],
    callback_url: Optional[str] = None,
):
    """Process large batches of data in the background"""
    try:
        if len(data) > 1000:
            # For large batches, process in background
            task_id = f"ai_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            background_tasks.add_task(_process_large_batch, data, task_id, callback_url)

            return {
                "task_id": task_id,
                "status": "processing",
                "message": f"Processing {len(data)} items in background",
            }
        else:
            # For smaller batches, process immediately
            processor = get_ai_processor()
            results = await processor.enhance_scraped_data(data)

            return {
                "status": "completed",
                "processed_count": len(results),
                "results": [
                    {
                        "quality_score": r.quality_score,
                        "entity_count": len(r.entities),
                        "category": r.classification.category,
                        "has_duplicates": bool(r.duplicates),
                    }
                    for r in results
                ],
            }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Batch processing failed: {str(e)}"
        )


async def _process_large_batch(
    data: List[Dict[str, Any]], task_id: str, callback_url: Optional[str]
):
    """Process large batch in background"""
    try:
        processor = get_ai_processor()
        results = await processor.enhance_scraped_data(data)

        # In a real implementation, you would save results to database
        # and optionally call the callback URL with results

        print(f"Batch {task_id} completed: {len(results)} items processed")

    except Exception as e:
        print(f"Batch {task_id} failed: {e}")


# Health check for AI system
@router.get("/health")
async def ai_health_check():
    """Check AI system health"""
    try:
        processor = get_ai_processor()
        status = processor.get_model_status()

        health_score = sum(status["capabilities"].values()) / len(
            status["capabilities"]
        )

        return {
            "status": "healthy" if health_score > 0.5 else "degraded",
            "ai_enabled": status["ai_enabled"],
            "capabilities_available": sum(status["capabilities"].values()),
            "total_capabilities": len(status["capabilities"]),
            "health_score": health_score,
        }

    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
