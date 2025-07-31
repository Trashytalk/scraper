"""
OCR Integration Module for Parsing Worker

Provides Optical Character Recognition capabilities for:
- Image files (JPEG, PNG, TIFF, BMP)
- PDF documents
- Screenshot processing
- Text extraction and URL discovery

Supports multiple OCR engines:
- Tesseract (free, open source)
- AWS Textract (cloud-based, high accuracy)
- Google Vision API (cloud-based)
- Azure Computer Vision (cloud-based)
"""

import asyncio
import io
import logging
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Tuple
from urllib.parse import urlparse
import base64

# Image processing
try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

# OCR engines
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

# Cloud OCR services
try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    boto3 = None

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    vision = None

try:
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
    from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
    AZURE_VISION_AVAILABLE = True
except ImportError:
    AZURE_VISION_AVAILABLE = False
    ComputerVisionClient = None

# PDF processing
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    pdf2image = None

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Result from OCR processing"""
    text: str
    confidence: float
    urls: List[str]
    bounding_boxes: List[Dict[str, Any]]
    processing_time_ms: int
    engine_used: str
    metadata: Dict[str, Any]


@dataclass
class OCRConfig:
    """Configuration for OCR processing"""
    engines: List[str] = None  # ['tesseract', 'aws_textract', 'google_vision', 'azure_vision']
    tesseract_config: str = "--psm 6"  # Page segmentation mode
    language: str = "eng"
    confidence_threshold: float = 0.7
    preprocess_images: bool = True
    extract_urls: bool = True
    max_image_size: Tuple[int, int] = (2048, 2048)
    
    def __post_init__(self):
        if self.engines is None:
            self.engines = ['tesseract']  # Default to Tesseract


class OCREngine:
    """Base class for OCR engines"""
    
    async def extract_text(self, image: Image.Image, config: OCRConfig) -> OCRResult:
        """Extract text from image"""
        raise NotImplementedError
    
    def preprocess_image(self, image: Image.Image, config: OCRConfig) -> Image.Image:
        """Preprocess image for better OCR results"""
        if not config.preprocess_images:
            return image
        
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            if image.size[0] > config.max_image_size[0] or image.size[1] > config.max_image_size[1]:
                image.thumbnail(config.max_image_size, Image.Resampling.LANCZOS)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            return image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {e}")
            return image
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract URLs from text using regex"""
        url_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}'
        ]
        
        urls = []
        for pattern in url_patterns:
            found_urls = re.findall(pattern, text, re.IGNORECASE)
            for url in found_urls:
                # Normalize URL
                if not url.startswith(('http://', 'https://')):
                    if url.startswith('www.'):
                        url = 'https://' + url
                    elif '.' in url and not url.startswith('mailto:'):
                        url = 'https://' + url
                
                # Validate URL
                try:
                    parsed = urlparse(url)
                    if parsed.netloc and parsed.scheme in ('http', 'https'):
                        urls.append(url)
                except Exception:
                    continue
        
        return list(set(urls))  # Remove duplicates


class TesseractOCREngine(OCREngine):
    """Tesseract OCR engine implementation"""
    
    def __init__(self):
        if not TESSERACT_AVAILABLE:
            raise ImportError("Tesseract not available. Install pytesseract: pip install pytesseract")
        if not PIL_AVAILABLE:
            raise ImportError("PIL not available. Install Pillow: pip install Pillow")
    
    async def extract_text(self, image: Image.Image, config: OCRConfig) -> OCRResult:
        """Extract text using Tesseract"""
        import time
        start_time = time.time()
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image, config)
            
            # Configure Tesseract
            tesseract_config = f"-l {config.language} {config.tesseract_config}"
            
            # Extract text and confidence data
            text_data = pytesseract.image_to_data(
                processed_image,
                config=tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Combine text and calculate average confidence
            text_parts = []
            confidences = []
            bounding_boxes = []
            
            for i in range(len(text_data['text'])):
                word = text_data['text'][i].strip()
                conf = int(text_data['conf'][i])
                
                if word and conf > 0:
                    text_parts.append(word)
                    confidences.append(conf)
                    
                    # Store bounding box
                    bounding_boxes.append({
                        'text': word,
                        'confidence': conf,
                        'left': text_data['left'][i],
                        'top': text_data['top'][i],
                        'width': text_data['width'][i],
                        'height': text_data['height'][i]
                    })
            
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract URLs
            urls = self.extract_urls_from_text(full_text) if config.extract_urls else []
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence / 100.0,  # Convert to 0-1 scale
                urls=urls,
                bounding_boxes=bounding_boxes,
                processing_time_ms=processing_time,
                engine_used="tesseract",
                metadata={
                    "tesseract_version": pytesseract.get_tesseract_version(),
                    "language": config.language,
                    "words_found": len(text_parts)
                }
            )
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                urls=[],
                bounding_boxes=[],
                processing_time_ms=int((time.time() - start_time) * 1000),
                engine_used="tesseract",
                metadata={"error": str(e)}
            )


class AWSTextractEngine(OCREngine):
    """AWS Textract OCR engine implementation"""
    
    def __init__(self, region_name: str = "us-west-2"):
        if not AWS_AVAILABLE:
            raise ImportError("AWS SDK not available. Install boto3: pip install boto3")
        
        self.textract_client = boto3.client('textract', region_name=region_name)
    
    async def extract_text(self, image: Image.Image, config: OCRConfig) -> OCRResult:
        """Extract text using AWS Textract"""
        import time
        start_time = time.time()
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image, config)
            
            # Convert image to bytes
            img_buffer = io.BytesIO()
            processed_image.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()
            
            # Call Textract
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.textract_client.detect_document_text(
                    Document={'Bytes': img_bytes}
                )
            )
            
            # Process response
            text_parts = []
            confidences = []
            bounding_boxes = []
            
            for block in response.get('Blocks', []):
                if block['BlockType'] == 'WORD':
                    text = block.get('Text', '')
                    confidence = block.get('Confidence', 0)
                    
                    if text and confidence > config.confidence_threshold * 100:
                        text_parts.append(text)
                        confidences.append(confidence)
                        
                        # Extract bounding box
                        bbox = block.get('Geometry', {}).get('BoundingBox', {})
                        bounding_boxes.append({
                            'text': text,
                            'confidence': confidence,
                            'left': bbox.get('Left', 0),
                            'top': bbox.get('Top', 0),
                            'width': bbox.get('Width', 0),
                            'height': bbox.get('Height', 0)
                        })
            
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract URLs
            urls = self.extract_urls_from_text(full_text) if config.extract_urls else []
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence / 100.0,
                urls=urls,
                bounding_boxes=bounding_boxes,
                processing_time_ms=processing_time,
                engine_used="aws_textract",
                metadata={
                    "blocks_processed": len(response.get('Blocks', [])),
                    "words_found": len(text_parts)
                }
            )
            
        except Exception as e:
            logger.error(f"AWS Textract OCR failed: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                urls=[],
                bounding_boxes=[],
                processing_time_ms=int((time.time() - start_time) * 1000),
                engine_used="aws_textract",
                metadata={"error": str(e)}
            )


class GoogleVisionEngine(OCREngine):
    """Google Vision API OCR engine implementation"""
    
    def __init__(self):
        if not GOOGLE_VISION_AVAILABLE:
            raise ImportError("Google Vision not available. Install google-cloud-vision")
        
        self.client = vision.ImageAnnotatorClient()
    
    async def extract_text(self, image: Image.Image, config: OCRConfig) -> OCRResult:
        """Extract text using Google Vision API"""
        import time
        start_time = time.time()
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image, config)
            
            # Convert image to bytes
            img_buffer = io.BytesIO()
            processed_image.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()
            
            # Create Vision API image object
            vision_image = vision.Image(content=img_bytes)
            
            # Call Vision API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.text_detection(image=vision_image)
            )
            
            texts = response.text_annotations
            
            if not texts:
                full_text = ""
                avg_confidence = 0.0
                bounding_boxes = []
            else:
                # First annotation contains the full text
                full_text = texts[0].description
                
                # Calculate average confidence from individual words
                confidences = []
                bounding_boxes = []
                
                for text in texts[1:]:  # Skip first (full text) annotation
                    # Google Vision doesn't provide confidence directly
                    # Use a heuristic based on bounding box regularity
                    vertices = text.bounding_poly.vertices
                    if len(vertices) == 4:
                        confidence = 85.0  # Assume good confidence for regular boxes
                    else:
                        confidence = 70.0  # Lower confidence for irregular shapes
                    
                    confidences.append(confidence)
                    
                    # Extract bounding box
                    if vertices:
                        min_x = min(v.x for v in vertices)
                        min_y = min(v.y for v in vertices)
                        max_x = max(v.x for v in vertices)
                        max_y = max(v.y for v in vertices)
                        
                        bounding_boxes.append({
                            'text': text.description,
                            'confidence': confidence,
                            'left': min_x,
                            'top': min_y,
                            'width': max_x - min_x,
                            'height': max_y - min_y
                        })
                
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract URLs
            urls = self.extract_urls_from_text(full_text) if config.extract_urls else []
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence / 100.0,
                urls=urls,
                bounding_boxes=bounding_boxes,
                processing_time_ms=processing_time,
                engine_used="google_vision",
                metadata={
                    "annotations_found": len(texts),
                    "has_error": bool(response.error.message) if response.error else False
                }
            )
            
        except Exception as e:
            logger.error(f"Google Vision OCR failed: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                urls=[],
                bounding_boxes=[],
                processing_time_ms=int((time.time() - start_time) * 1000),
                engine_used="google_vision",
                metadata={"error": str(e)}
            )


class OCRProcessor:
    """Main OCR processor that coordinates multiple engines"""
    
    def __init__(self, config: OCRConfig = None):
        self.config = config or OCRConfig()
        self.engines = {}
        
        # Initialize available engines
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize available OCR engines"""
        for engine_name in self.config.engines:
            try:
                if engine_name == "tesseract" and TESSERACT_AVAILABLE:
                    self.engines["tesseract"] = TesseractOCREngine()
                elif engine_name == "aws_textract" and AWS_AVAILABLE:
                    self.engines["aws_textract"] = AWSTextractEngine()
                elif engine_name == "google_vision" and GOOGLE_VISION_AVAILABLE:
                    self.engines["google_vision"] = GoogleVisionEngine()
                # Add Azure Vision when implemented
                else:
                    logger.warning(f"OCR engine '{engine_name}' not available")
            except Exception as e:
                logger.error(f"Failed to initialize OCR engine '{engine_name}': {e}")
        
        if not self.engines:
            logger.warning("No OCR engines available")
    
    async def process_image(self, image_data: bytes, content_type: str = "image/jpeg") -> OCRResult:
        """Process image data and extract text"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Try engines in order of preference
            best_result = None
            
            for engine_name, engine in self.engines.items():
                try:
                    result = await engine.extract_text(image, self.config)
                    
                    # Use result if it meets confidence threshold
                    if result.confidence >= self.config.confidence_threshold:
                        return result
                    
                    # Keep track of best result so far
                    if best_result is None or result.confidence > best_result.confidence:
                        best_result = result
                        
                except Exception as e:
                    logger.warning(f"OCR engine '{engine_name}' failed: {e}")
                    continue
            
            # Return best result or empty result
            return best_result or OCRResult(
                text="",
                confidence=0.0,
                urls=[],
                bounding_boxes=[],
                processing_time_ms=0,
                engine_used="none",
                metadata={"error": "No engines succeeded"}
            )
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                urls=[],
                bounding_boxes=[],
                processing_time_ms=0,
                engine_used="none",
                metadata={"error": str(e)}
            )
    
    async def process_pdf(self, pdf_data: bytes, max_pages: int = 10) -> List[OCRResult]:
        """Process PDF and extract text from each page"""
        if not PYMUPDF_AVAILABLE and not PDF2IMAGE_AVAILABLE:
            logger.error("PDF processing not available. Install PyMuPDF or pdf2image")
            return []
        
        results = []
        
        try:
            if PYMUPDF_AVAILABLE:
                # Use PyMuPDF for PDF processing
                pdf_doc = fitz.open("pdf", pdf_data)
                
                for page_num in range(min(len(pdf_doc), max_pages)):
                    page = pdf_doc[page_num]
                    
                    # Convert page to image
                    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    
                    # Process with OCR
                    result = await self.process_image(img_data, "image/png")
                    result.metadata["page_number"] = page_num + 1
                    result.metadata["total_pages"] = len(pdf_doc)
                    
                    results.append(result)
                
                pdf_doc.close()
                
            elif PDF2IMAGE_AVAILABLE:
                # Use pdf2image as fallback
                images = pdf2image.convert_from_bytes(
                    pdf_data,
                    first_page=1,
                    last_page=max_pages,
                    dpi=200
                )
                
                for page_num, image in enumerate(images):
                    # Convert PIL image to bytes
                    img_buffer = io.BytesIO()
                    image.save(img_buffer, format='PNG')
                    img_data = img_buffer.getvalue()
                    
                    # Process with OCR
                    result = await self.process_image(img_data, "image/png")
                    result.metadata["page_number"] = page_num + 1
                    result.metadata["total_pages"] = len(images)
                    
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"PDF OCR processing failed: {e}")
            return []
    
    def get_available_engines(self) -> List[str]:
        """Get list of available OCR engines"""
        return list(self.engines.keys())
    
    def get_engine_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get capabilities of each available engine"""
        capabilities = {}
        
        if "tesseract" in self.engines:
            capabilities["tesseract"] = {
                "free": True,
                "offline": True,
                "languages": "100+",
                "confidence_scores": True,
                "bounding_boxes": True,
                "best_for": "General text, offline processing"
            }
        
        if "aws_textract" in self.engines:
            capabilities["aws_textract"] = {
                "free": False,
                "offline": False,
                "languages": "Limited",
                "confidence_scores": True,
                "bounding_boxes": True,
                "best_for": "Documents, forms, high accuracy"
            }
        
        if "google_vision" in self.engines:
            capabilities["google_vision"] = {
                "free": "Limited",
                "offline": False,
                "languages": "50+",
                "confidence_scores": False,
                "bounding_boxes": True,
                "best_for": "Natural images, handwriting"
            }
        
        return capabilities


# Factory function for easy OCR setup
def create_ocr_processor(
    engines: List[str] = None,
    language: str = "eng",
    confidence_threshold: float = 0.7,
    **kwargs
) -> OCRProcessor:
    """Create OCR processor with specified configuration"""
    
    # Default to available engines if none specified
    if engines is None:
        engines = []
        if TESSERACT_AVAILABLE:
            engines.append("tesseract")
        if AWS_AVAILABLE:
            engines.append("aws_textract")
        if GOOGLE_VISION_AVAILABLE:
            engines.append("google_vision")
    
    config = OCRConfig(
        engines=engines,
        language=language,
        confidence_threshold=confidence_threshold,
        **kwargs
    )
    
    return OCRProcessor(config)


# Example usage
async def example_ocr_usage():
    """Example of how to use the OCR system"""
    
    # Create OCR processor with preferred engines
    ocr = create_ocr_processor(
        engines=["tesseract", "aws_textract"],
        language="eng",
        confidence_threshold=0.8
    )
    
    # Process an image
    with open("sample_image.jpg", "rb") as f:
        image_data = f.read()
    
    result = await ocr.process_image(image_data)
    
    print(f"Extracted text: {result.text}")
    print(f"Confidence: {result.confidence}")
    print(f"URLs found: {result.urls}")
    print(f"Engine used: {result.engine_used}")
    
    # Process a PDF
    with open("sample_document.pdf", "rb") as f:
        pdf_data = f.read()
    
    pdf_results = await ocr.process_pdf(pdf_data, max_pages=5)
    
    for i, result in enumerate(pdf_results):
        print(f"Page {i+1}: {len(result.text)} characters, {len(result.urls)} URLs")


if __name__ == "__main__":
    asyncio.run(example_ocr_usage())
