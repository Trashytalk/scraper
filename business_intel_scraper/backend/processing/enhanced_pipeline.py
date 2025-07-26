"""
Enhanced Data Processing Pipeline with Advanced Parsing Integration
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field

from gui.components.advanced_parsing import (
    AdvancedParser,
    ParsingRule,
    FileFormat,
    ParsingMode,
)
from business_intel_scraper.backend.nlp.pipeline import extract_entities
from business_intel_scraper.backend.nlp.cleaning import clean_text
from business_intel_scraper.backend.db.pipeline import DatabasePipeline

logger = logging.getLogger(__name__)


@dataclass
class ProcessingTask:
    """Data processing task configuration"""

    task_id: str
    input_data: Union[str, List[str], Dict[str, Any]]
    input_format: FileFormat = FileFormat.TEXT
    parsing_rules: List[ParsingRule] = field(default_factory=list)
    processing_mode: ParsingMode = ParsingMode.BATCH
    output_format: str = "json"
    destination: Optional[str] = None
    callback: Optional[Callable] = None
    status: str = "pending"
    progress: float = 0.0
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class EnhancedDataProcessor:
    """Enhanced data processor with integrated parsing and NLP"""

    def __init__(self):
        self.advanced_parser = AdvancedParser()
        self.db_pipeline = DatabasePipeline()
        self.processing_queue: List[ProcessingTask] = []
        self.active_tasks: Dict[str, ProcessingTask] = {}
        self.processing_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "entities_extracted": 0,
            "documents_parsed": 0,
        }

    async def submit_task(self, task: ProcessingTask) -> str:
        """Submit a data processing task"""
        try:
            task.status = "queued"
            self.processing_queue.append(task)
            logger.info(f"Task {task.task_id} submitted for processing")

            # Process immediately if in real-time mode
            if task.processing_mode == ParsingMode.REALTIME:
                await self.process_task(task)

            return task.task_id

        except Exception as e:
            logger.error(f"Error submitting task {task.task_id}: {e}")
            task.status = "error"
            task.error = str(e)
            raise

    async def process_task(self, task: ProcessingTask) -> Dict[str, Any]:
        """Process a single data processing task"""
        try:
            task.status = "processing"
            self.active_tasks[task.task_id] = task
            task.progress = 0.0

            logger.info(f"Processing task {task.task_id}")

            # Step 1: Parse input data
            task.progress = 0.1
            parsed_data = await self._parse_input_data(task)

            if not parsed_data:
                raise ValueError("Failed to parse input data")

            # Step 2: Apply parsing rules
            task.progress = 0.3
            rule_results = await self._apply_parsing_rules(
                parsed_data, task.parsing_rules
            )

            # Step 3: Extract entities using NLP
            task.progress = 0.5
            nlp_results = await self._extract_entities(parsed_data)

            # Step 4: Clean and normalize data
            task.progress = 0.7
            cleaned_data = await self._clean_and_normalize(
                parsed_data, rule_results, nlp_results
            )

            # Step 5: Store results
            task.progress = 0.9
            storage_result = await self._store_results(task, cleaned_data)

            # Complete task
            task.progress = 1.0
            task.status = "completed"
            task.results = cleaned_data

            # Update statistics
            self.processing_stats["total_processed"] += 1
            self.processing_stats["successful"] += 1
            self.processing_stats["entities_extracted"] += len(
                nlp_results.get("entities", [])
            )
            self.processing_stats["documents_parsed"] += 1

            logger.info(f"Task {task.task_id} completed successfully")

            # Execute callback if provided
            if task.callback:
                try:
                    task.callback(task.task_id, cleaned_data)
                except Exception as e:
                    logger.warning(f"Task callback error: {e}")

            return cleaned_data

        except Exception as e:
            logger.error(f"Error processing task {task.task_id}: {e}")
            task.status = "error"
            task.error = str(e)
            self.processing_stats["failed"] += 1
            raise

        finally:
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]

    async def _parse_input_data(self, task: ProcessingTask) -> Dict[str, Any]:
        """Parse input data using advanced parser"""
        try:
            if isinstance(task.input_data, str):
                if Path(task.input_data).exists():
                    # File input
                    return self.advanced_parser.parse_file(
                        task.input_data, task.input_format, task.parsing_rules
                    )
                else:
                    # Text input
                    return self.advanced_parser._apply_parsing_rules(
                        task.input_data, task.parsing_rules
                    )
            elif isinstance(task.input_data, list):
                # Multiple inputs - batch processing
                results = []
                for i, input_item in enumerate(task.input_data):
                    if isinstance(input_item, str):
                        if Path(input_item).exists():
                            result = self.advanced_parser.parse_file(
                                input_item, task.input_format, task.parsing_rules
                            )
                        else:
                            result = self.advanced_parser._apply_parsing_rules(
                                input_item, task.parsing_rules
                            )
                        results.append(result)

                        # Update progress
                        task.progress = 0.1 + (i / len(task.input_data)) * 0.2

                return {"batch_results": results}
            else:
                # Dictionary input
                return {"structured_data": task.input_data}

        except Exception as e:
            logger.error(f"Error parsing input data: {e}")
            raise

    async def _apply_parsing_rules(
        self, parsed_data: Dict[str, Any], rules: List[ParsingRule]
    ) -> Dict[str, Any]:
        """Apply additional parsing rules to extracted data"""
        try:
            rule_results = {}

            # Get raw content from parsed data
            raw_content = parsed_data.get("raw_content", "")
            if not raw_content and "batch_results" in parsed_data:
                # Combine content from batch results
                raw_content = " ".join(
                    [
                        result.get("raw_content", "")
                        for result in parsed_data["batch_results"]
                        if "raw_content" in result
                    ]
                )

            if raw_content:
                for rule in rules:
                    if rule.enabled:
                        extracted = self.advanced_parser._extract_by_rule(
                            raw_content, rule
                        )
                        if extracted:
                            rule_results[rule.name] = {
                                "data": extracted,
                                "confidence": rule.confidence_threshold,
                                "rule_type": rule.extraction_type,
                            }

            return rule_results

        except Exception as e:
            logger.error(f"Error applying parsing rules: {e}")
            return {}

    async def _extract_entities(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entities using NLP pipeline"""
        try:
            # Get text content
            text_content = self._extract_text_content(parsed_data)

            if not text_content:
                return {"entities": []}

            # Use existing NLP pipeline
            entities = extract_entities([text_content])

            # Add ML-based entity extraction if available
            ml_results = {}
            if hasattr(self.advanced_parser, "_apply_ml_models"):
                ml_results = self.advanced_parser._apply_ml_models(text_content)

            return {
                "entities": entities,
                "ml_entities": ml_results.get("entities", []),
                "spacy_entities": ml_results.get("spacy_entities", []),
                "classification": ml_results.get("classification", []),
                "summary": ml_results.get("summary"),
            }

        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {"entities": []}

    async def _clean_and_normalize(
        self,
        parsed_data: Dict[str, Any],
        rule_results: Dict[str, Any],
        nlp_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Clean and normalize extracted data"""
        try:
            # Get raw content
            text_content = self._extract_text_content(parsed_data)

            # Clean text using existing pipeline
            cleaned_text = clean_text(text_content) if text_content else ""

            # Combine all results
            consolidated_results = {
                "original_data": parsed_data,
                "cleaned_text": cleaned_text,
                "extracted_data": parsed_data.get("extracted_data", {}),
                "rule_results": rule_results,
                "entities": nlp_results.get("entities", []),
                "ml_entities": nlp_results.get("ml_entities", []),
                "spacy_entities": nlp_results.get("spacy_entities", []),
                "classification": nlp_results.get("classification", []),
                "summary": nlp_results.get("summary"),
                "metadata": {
                    "processing_timestamp": asyncio.get_event_loop().time(),
                    "content_length": len(text_content) if text_content else 0,
                    "entity_count": len(nlp_results.get("entities", [])),
                    "rule_matches": len(rule_results),
                },
            }

            return consolidated_results

        except Exception as e:
            logger.error(f"Error cleaning and normalizing data: {e}")
            raise

    async def _store_results(
        self, task: ProcessingTask, results: Dict[str, Any]
    ) -> bool:
        """Store processing results"""
        try:
            # Store in database if configured
            if hasattr(self.db_pipeline, "store_processed_data"):
                await self.db_pipeline.store_processed_data(task.task_id, results)

            # Export to file if destination specified
            if task.destination:
                await self._export_results(
                    results, task.destination, task.output_format
                )

            return True

        except Exception as e:
            logger.error(f"Error storing results: {e}")
            return False

    async def _export_results(
        self, results: Dict[str, Any], destination: str, format: str
    ):
        """Export results to file"""
        try:
            output_path = Path(destination)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if format.lower() == "json":
                import json

                with open(output_path, "w") as f:
                    json.dump(results, f, indent=2, default=str)
            elif format.lower() == "csv":
                import pandas as pd

                # Flatten results for CSV export
                flattened = self._flatten_results(results)
                df = pd.DataFrame([flattened])
                df.to_csv(output_path, index=False)
            else:
                # Default to JSON
                import json

                with open(output_path, "w") as f:
                    json.dump(results, f, indent=2, default=str)

            logger.info(f"Results exported to {destination}")

        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            raise

    def _extract_text_content(self, parsed_data: Dict[str, Any]) -> str:
        """Extract text content from parsed data"""
        # Try different content sources
        if "raw_content" in parsed_data:
            return parsed_data["raw_content"]
        elif "batch_results" in parsed_data:
            return " ".join(
                [
                    result.get("raw_content", "")
                    for result in parsed_data["batch_results"]
                    if "raw_content" in result
                ]
            )
        elif "structured_data" in parsed_data:
            return str(parsed_data["structured_data"])
        else:
            return ""

    def _flatten_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested results for CSV export"""
        flattened = {}

        # Basic fields
        flattened["cleaned_text"] = results.get("cleaned_text", "")
        flattened["entity_count"] = len(results.get("entities", []))
        flattened["ml_entity_count"] = len(results.get("ml_entities", []))
        flattened["classification"] = str(results.get("classification", []))
        flattened["summary"] = results.get("summary", "")

        # Metadata
        metadata = results.get("metadata", {})
        for key, value in metadata.items():
            flattened[f"meta_{key}"] = value

        # Rule results
        rule_results = results.get("rule_results", {})
        for rule_name, rule_data in rule_results.items():
            flattened[f"rule_{rule_name}"] = str(rule_data.get("data", ""))

        return flattened

    async def process_queue(self):
        """Process all queued tasks"""
        while self.processing_queue:
            task = self.processing_queue.pop(0)
            try:
                await self.process_task(task)
            except Exception as e:
                logger.error(f"Failed to process queued task {task.task_id}: {e}")

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a processing task"""
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "task_id": task.task_id,
                "status": task.status,
                "progress": task.progress,
                "error": task.error,
            }

        # Check queued tasks
        for task in self.processing_queue:
            if task.task_id == task_id:
                return {
                    "task_id": task.task_id,
                    "status": task.status,
                    "progress": task.progress,
                    "error": task.error,
                }

        return None

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.processing_stats,
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.processing_queue),
        }


# Global enhanced data processor instance
data_processor = EnhancedDataProcessor()
