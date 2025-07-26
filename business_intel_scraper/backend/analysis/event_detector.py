"""
Business Event Detection System

Monitors and detects significant business events:
- Ownership changes and acquisitions
- New regulatory filings
- Contract awards and terminations
- Executive changes
- Address/location changes
- Legal proceedings and sanctions
- Financial events (IPOs, bankruptcies)
- Negative news and media coverage
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import hashlib
import re

logger = logging.getLogger(__name__)


class EventSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventCategory(Enum):
    OWNERSHIP = "ownership"
    REGULATORY = "regulatory"
    CONTRACTS = "contracts"
    EXECUTIVE = "executive"
    LOCATION = "location"
    LEGAL = "legal"
    FINANCIAL = "financial"
    REPUTATION = "reputation"
    OPERATIONAL = "operational"


@dataclass
class BusinessEvent:
    """Container for detected business events"""

    event_id: str
    entity_id: str
    event_type: str
    category: EventCategory
    severity: EventSeverity
    title: str
    description: str
    event_date: datetime
    detection_date: datetime
    confidence_score: float
    source: str
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_entities: List[str] = field(default_factory=list)
    impact_assessment: Optional[Dict[str, Any]] = None


@dataclass
class EventPattern:
    """Pattern definition for event detection"""

    pattern_id: str
    category: EventCategory
    severity: EventSeverity
    keywords: List[str]
    regex_patterns: List[str]
    context_requirements: List[str]
    confidence_threshold: float = 0.7
    enabled: bool = True


class BusinessEventDetector:
    """Advanced business event detection and monitoring system"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.event_patterns = self._initialize_event_patterns()
        self.detection_history = {}
        self.subscribers = {}  # Event notification subscribers

        # Detection metrics
        self.detection_metrics = {
            "total_scanned": 0,
            "events_detected": 0,
            "false_positives": 0,
            "alerts_sent": 0,
            "last_scan": None,
        }

        # Recent events cache for deduplication
        self.recent_events = {}
        self.deduplication_window = timedelta(hours=24)

    def _initialize_event_patterns(self) -> Dict[str, EventPattern]:
        """Initialize event detection patterns"""
        patterns = {}

        # Ownership change patterns
        patterns["ownership_acquisition"] = EventPattern(
            pattern_id="ownership_acquisition",
            category=EventCategory.OWNERSHIP,
            severity=EventSeverity.HIGH,
            keywords=["acquisition", "merger", "acquired", "buyout", "takeover"],
            regex_patterns=[
                r"(?i)acquired?\s+by\s+[\w\s]+",
                r"(?i)merger\s+with\s+[\w\s]+",
                r"(?i)[\w\s]+\s+acquires?\s+[\w\s]+",
                r"(?i)takeover\s+of\s+[\w\s]+",
                r"(?i)bought\s+by\s+[\w\s]+",
            ],
            context_requirements=["company", "business", "corporation"],
            confidence_threshold=0.8,
        )

        patterns["ownership_change"] = EventPattern(
            pattern_id="ownership_change",
            category=EventCategory.OWNERSHIP,
            severity=EventSeverity.MEDIUM,
            keywords=["ownership", "shares", "stake", "equity", "investment"],
            regex_patterns=[
                r"(?i)(\d+)%\s+stake",
                r"(?i)increased\s+ownership",
                r"(?i)reduced\s+stake",
                r"(?i)new\s+investor",
                r"(?i)equity\s+investment",
            ],
            context_requirements=["company", "investment"],
            confidence_threshold=0.7,
        )

        # Regulatory filing patterns
        patterns["sec_filing"] = EventPattern(
            pattern_id="sec_filing",
            category=EventCategory.REGULATORY,
            severity=EventSeverity.MEDIUM,
            keywords=["SEC filing", "10-K", "10-Q", "8-K", "proxy statement"],
            regex_patterns=[
                r"(?i)filed?\s+(10-[KQ]|8-K)",
                r"(?i)SEC\s+filing",
                r"(?i)proxy\s+statement",
                r"(?i)annual\s+report",
                r"(?i)quarterly\s+report",
            ],
            context_requirements=["SEC", "filing"],
            confidence_threshold=0.9,
        )

        patterns["regulatory_action"] = EventPattern(
            pattern_id="regulatory_action",
            category=EventCategory.REGULATORY,
            severity=EventSeverity.HIGH,
            keywords=["fined", "penalty", "violation", "sanctions", "investigation"],
            regex_patterns=[
                r"(?i)fined\s+\$[\d,]+",
                r"(?i)penalty\s+of\s+\$[\d,]+",
                r"(?i)regulatory\s+violation",
                r"(?i)under\s+investigation",
                r"(?i)sanctioned\s+by",
            ],
            context_requirements=["regulatory", "fine", "penalty"],
            confidence_threshold=0.8,
        )

        # Contract patterns
        patterns["contract_award"] = EventPattern(
            pattern_id="contract_award",
            category=EventCategory.CONTRACTS,
            severity=EventSeverity.MEDIUM,
            keywords=["contract", "awarded", "won", "selected", "procurement"],
            regex_patterns=[
                r"(?i)awarded\s+\$[\d,.]+\s+contract",
                r"(?i)won\s+[\w\s]+\s+contract",
                r"(?i)selected\s+for\s+[\w\s]+\s+project",
                r"(?i)\$[\d,.]+\s+contract\s+with",
                r"(?i)procurement\s+contract",
            ],
            context_requirements=["contract", "award"],
            confidence_threshold=0.8,
        )

        patterns["contract_termination"] = EventPattern(
            pattern_id="contract_termination",
            category=EventCategory.CONTRACTS,
            severity=EventSeverity.HIGH,
            keywords=["terminated", "cancelled", "suspended", "breach"],
            regex_patterns=[
                r"(?i)contract\s+terminated",
                r"(?i)contract\s+cancelled",
                r"(?i)contract\s+suspended",
                r"(?i)breach\s+of\s+contract",
                r"(?i)contract\s+dispute",
            ],
            context_requirements=["contract", "termination"],
            confidence_threshold=0.8,
        )

        # Executive change patterns
        patterns["executive_change"] = EventPattern(
            pattern_id="executive_change",
            category=EventCategory.EXECUTIVE,
            severity=EventSeverity.MEDIUM,
            keywords=["CEO", "president", "director", "resigned", "appointed"],
            regex_patterns=[
                r"(?i)(CEO|president|director)\s+(resigned|left|departed)",
                r"(?i)appointed\s+(CEO|president|director)",
                r"(?i)new\s+(CEO|president|director)",
                r"(?i)(CEO|president|director)\s+replacement",
                r"(?i)leadership\s+change",
            ],
            context_requirements=["executive", "leadership"],
            confidence_threshold=0.8,
        )

        # Legal proceedings patterns
        patterns["lawsuit"] = EventPattern(
            pattern_id="lawsuit",
            category=EventCategory.LEGAL,
            severity=EventSeverity.HIGH,
            keywords=["lawsuit", "sued", "litigation", "court", "legal action"],
            regex_patterns=[
                r"(?i)filed\s+lawsuit",
                r"(?i)sued\s+for\s+\$[\d,.]+",
                r"(?i)legal\s+action\s+against",
                r"(?i)court\s+case",
                r"(?i)litigation\s+involving",
            ],
            context_requirements=["legal", "lawsuit"],
            confidence_threshold=0.8,
        )

        # Financial event patterns
        patterns["financial_distress"] = EventPattern(
            pattern_id="financial_distress",
            category=EventCategory.FINANCIAL,
            severity=EventSeverity.CRITICAL,
            keywords=["bankruptcy", "insolvent", "default", "financial distress"],
            regex_patterns=[
                r"(?i)filed\s+for\s+bankruptcy",
                r"(?i)chapter\s+11",
                r"(?i)financial\s+distress",
                r"(?i)default\s+on\s+debt",
                r"(?i)insolvent",
            ],
            context_requirements=["financial", "bankruptcy"],
            confidence_threshold=0.9,
        )

        patterns["ipo_announcement"] = EventPattern(
            pattern_id="ipo_announcement",
            category=EventCategory.FINANCIAL,
            severity=EventSeverity.MEDIUM,
            keywords=["IPO", "public offering", "going public", "stock market"],
            regex_patterns=[
                r"(?i)initial\s+public\s+offering",
                r"(?i)going\s+public",
                r"(?i)IPO\s+filing",
                r"(?i)public\s+offering",
                r"(?i)stock\s+market\s+debut",
            ],
            context_requirements=["IPO", "public"],
            confidence_threshold=0.8,
        )

        # Reputation/negative news patterns
        patterns["negative_news"] = EventPattern(
            pattern_id="negative_news",
            category=EventCategory.REPUTATION,
            severity=EventSeverity.MEDIUM,
            keywords=["scandal", "controversy", "investigation", "fraud", "misconduct"],
            regex_patterns=[
                r"(?i)scandal\s+involving",
                r"(?i)controversy\s+over",
                r"(?i)accused\s+of\s+fraud",
                r"(?i)misconduct\s+allegations",
                r"(?i)under\s+investigation\s+for",
            ],
            context_requirements=["negative", "scandal", "investigation"],
            confidence_threshold=0.7,
        )

        return patterns

    async def detect_events(
        self, data_sources: List[Dict[str, Any]], entities: Optional[List[str]] = None
    ) -> List[BusinessEvent]:
        """Main event detection pipeline"""
        logger.info(f"Starting event detection across {len(data_sources)} data sources")

        all_events = []

        for source in data_sources:
            source_events = await self._detect_events_in_source(source, entities)
            all_events.extend(source_events)

        # Remove duplicates
        unique_events = self._deduplicate_events(all_events)

        # Update metrics
        self.detection_metrics["total_scanned"] += len(data_sources)
        self.detection_metrics["events_detected"] += len(unique_events)
        self.detection_metrics["last_scan"] = datetime.utcnow()

        # Send notifications for high-severity events
        await self._send_event_notifications(unique_events)

        logger.info(
            f"Event detection completed. Found {len(unique_events)} unique events"
        )
        return unique_events

    async def _detect_events_in_source(
        self, source: Dict[str, Any], entities: Optional[List[str]]
    ) -> List[BusinessEvent]:
        """Detect events in a single data source"""
        events = []
        source_type = source.get("type", "unknown")
        source_data = source.get("data", [])
        source_url = source.get("url")

        if source_type == "news_articles":
            events.extend(
                await self._detect_news_events(source_data, source_url, entities)
            )
        elif source_type == "filings":
            events.extend(
                await self._detect_filing_events(source_data, source_url, entities)
            )
        elif source_type == "contracts":
            events.extend(
                await self._detect_contract_events(source_data, source_url, entities)
            )
        elif source_type == "social_media":
            events.extend(
                await self._detect_social_events(source_data, source_url, entities)
            )
        elif source_type == "structured_data":
            events.extend(
                await self._detect_structured_events(source_data, source_url, entities)
            )

        return events

    async def _detect_news_events(
        self,
        articles: List[Dict],
        source_url: Optional[str],
        entities: Optional[List[str]],
    ) -> List[BusinessEvent]:
        """Detect events from news articles"""
        events = []

        for article in articles:
            title = article.get("title", "")
            content = article.get("content", "")
            published_date = article.get("published_date")
            article_url = article.get("url", source_url)

            # Combine title and content for analysis
            text = f"{title} {content}".lower()

            # Check each pattern
            for pattern_id, pattern in self.event_patterns.items():
                if not pattern.enabled:
                    continue

                event = await self._check_pattern_match(
                    text, article, pattern, source_url, entities
                )

                if event:
                    event.source = "news"
                    event.source_url = article_url
                    if published_date:
                        event.event_date = published_date
                    events.append(event)

        return events

    async def _detect_filing_events(
        self,
        filings: List[Dict],
        source_url: Optional[str],
        entities: Optional[List[str]],
    ) -> List[BusinessEvent]:
        """Detect events from regulatory filings"""
        events = []

        for filing in filings:
            filing_type = filing.get("type", "")
            filing_text = filing.get("content", "")
            filing_date = filing.get("date")
            entity_id = filing.get("entity_id", "")

            # Focus on regulatory patterns for filings
            regulatory_patterns = {
                k: v
                for k, v in self.event_patterns.items()
                if v.category == EventCategory.REGULATORY
            }

            for pattern_id, pattern in regulatory_patterns.items():
                if not pattern.enabled:
                    continue

                event = await self._check_pattern_match(
                    filing_text, filing, pattern, source_url, entities
                )

                if event:
                    event.source = "regulatory_filing"
                    event.entity_id = entity_id
                    if filing_date:
                        event.event_date = filing_date
                    events.append(event)

        return events

    async def _detect_contract_events(
        self,
        contracts: List[Dict],
        source_url: Optional[str],
        entities: Optional[List[str]],
    ) -> List[BusinessEvent]:
        """Detect events from contract data"""
        events = []

        for contract in contracts:
            contract_text = contract.get("description", "")
            contract_status = contract.get("status", "")
            contract_date = contract.get("date")
            entity_id = contract.get("entity_id", "")

            # Focus on contract patterns
            contract_patterns = {
                k: v
                for k, v in self.event_patterns.items()
                if v.category == EventCategory.CONTRACTS
            }

            for pattern_id, pattern in contract_patterns.items():
                if not pattern.enabled:
                    continue

                event = await self._check_pattern_match(
                    contract_text, contract, pattern, source_url, entities
                )

                if event:
                    event.source = "contract_data"
                    event.entity_id = entity_id
                    if contract_date:
                        event.event_date = contract_date
                    events.append(event)

        return events

    async def _detect_social_events(
        self,
        posts: List[Dict],
        source_url: Optional[str],
        entities: Optional[List[str]],
    ) -> List[BusinessEvent]:
        """Detect events from social media posts"""
        events = []

        # Social media detection would focus on reputation events
        reputation_patterns = {
            k: v
            for k, v in self.event_patterns.items()
            if v.category == EventCategory.REPUTATION
        }

        for post in posts:
            post_text = post.get("text", "")
            post_date = post.get("date")

            for pattern_id, pattern in reputation_patterns.items():
                if not pattern.enabled:
                    continue

                event = await self._check_pattern_match(
                    post_text, post, pattern, source_url, entities
                )

                if event:
                    event.source = "social_media"
                    if post_date:
                        event.event_date = post_date
                    events.append(event)

        return events

    async def _detect_structured_events(
        self,
        records: List[Dict],
        source_url: Optional[str],
        entities: Optional[List[str]],
    ) -> List[BusinessEvent]:
        """Detect events from structured data"""
        events = []

        for record in records:
            # Structured data can contain various event types
            record_text = " ".join(
                str(v) for v in record.values() if isinstance(v, (str, int, float))
            )
            record_date = record.get("date") or record.get("timestamp")
            entity_id = record.get("entity_id", "")

            for pattern_id, pattern in self.event_patterns.items():
                if not pattern.enabled:
                    continue

                event = await self._check_pattern_match(
                    record_text, record, pattern, source_url, entities
                )

                if event:
                    event.source = "structured_data"
                    event.entity_id = entity_id
                    if record_date:
                        event.event_date = record_date
                    events.append(event)

        return events

    async def _check_pattern_match(
        self,
        text: str,
        source_data: Dict,
        pattern: EventPattern,
        source_url: Optional[str],
        entities: Optional[List[str]],
    ) -> Optional[BusinessEvent]:
        """Check if text matches a specific event pattern"""
        confidence_score = 0.0
        matched_keywords = []
        matched_patterns = []

        # Check keyword matches
        for keyword in pattern.keywords:
            if keyword.lower() in text.lower():
                matched_keywords.append(keyword)
                confidence_score += 0.3

        # Check regex patterns
        for regex_pattern in pattern.regex_patterns:
            try:
                if re.search(regex_pattern, text):
                    matched_patterns.append(regex_pattern)
                    confidence_score += 0.5
            except re.error:
                logger.error(f"Invalid regex pattern: {regex_pattern}")
                continue

        # Check context requirements
        context_matches = 0
        for context in pattern.context_requirements:
            if context.lower() in text.lower():
                context_matches += 1

        if context_matches > 0:
            confidence_score += 0.2 * (
                context_matches / len(pattern.context_requirements)
            )

        # Normalize confidence score
        confidence_score = min(confidence_score, 1.0)

        # Check if confidence meets threshold
        if confidence_score < pattern.confidence_threshold:
            return None

        # Create event
        event_id = self._generate_event_id(text, pattern.pattern_id)
        entity_id = source_data.get("entity_id", "")

        # Extract entity mentions if entities list provided
        related_entities = []
        if entities:
            for entity in entities:
                if entity.lower() in text.lower():
                    related_entities.append(entity)

        event = BusinessEvent(
            event_id=event_id,
            entity_id=entity_id,
            event_type=pattern.pattern_id,
            category=pattern.category,
            severity=pattern.severity,
            title=self._generate_event_title(text, pattern),
            description=text[:500],  # Truncate for storage
            event_date=datetime.utcnow(),  # Will be overridden if actual date available
            detection_date=datetime.utcnow(),
            confidence_score=confidence_score,
            source="unknown",  # Will be overridden by caller
            source_url=source_url,
            metadata={
                "matched_keywords": matched_keywords,
                "matched_patterns": matched_patterns,
                "context_matches": context_matches,
                "pattern_id": pattern.pattern_id,
            },
            related_entities=related_entities,
        )

        return event

    def _generate_event_id(self, text: str, pattern_id: str) -> str:
        """Generate unique event ID"""
        content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{pattern_id}_{timestamp}_{content_hash}"

    def _generate_event_title(self, text: str, pattern: EventPattern) -> str:
        """Generate descriptive event title"""
        # Extract first sentence or meaningful portion
        sentences = text.split(".")
        title = sentences[0][:100] if sentences else text[:100]

        # Add pattern category context
        category_titles = {
            EventCategory.OWNERSHIP: "Ownership Change",
            EventCategory.REGULATORY: "Regulatory Event",
            EventCategory.CONTRACTS: "Contract Event",
            EventCategory.EXECUTIVE: "Executive Change",
            EventCategory.LOCATION: "Location Change",
            EventCategory.LEGAL: "Legal Event",
            EventCategory.FINANCIAL: "Financial Event",
            EventCategory.REPUTATION: "Reputation Event",
            EventCategory.OPERATIONAL: "Operational Event",
        }

        category_title = category_titles.get(pattern.category, "Business Event")
        return f"{category_title}: {title}"

    def _deduplicate_events(self, events: List[BusinessEvent]) -> List[BusinessEvent]:
        """Remove duplicate events within the deduplication window"""
        unique_events = []
        event_signatures = set()

        for event in events:
            # Create signature for deduplication
            signature = (
                f"{event.entity_id}_{event.event_type}_{event.event_date.date()}"
            )

            if signature not in event_signatures:
                event_signatures.add(signature)
                unique_events.append(event)
            else:
                logger.debug(f"Duplicate event filtered: {signature}")

        return unique_events

    async def _send_event_notifications(self, events: List[BusinessEvent]):
        """Send notifications for significant events"""
        high_severity_events = [
            e
            for e in events
            if e.severity in [EventSeverity.HIGH, EventSeverity.CRITICAL]
        ]

        for event in high_severity_events:
            await self._notify_subscribers(event)
            self.detection_metrics["alerts_sent"] += 1

    async def _notify_subscribers(self, event: BusinessEvent):
        """Notify subscribers about an event"""
        for subscriber_id, callback in self.subscribers.items():
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error notifying subscriber {subscriber_id}: {e}")

    def subscribe_to_events(self, subscriber_id: str, callback: Callable):
        """Subscribe to event notifications"""
        self.subscribers[subscriber_id] = callback
        logger.info(f"Subscriber {subscriber_id} registered for event notifications")

    def unsubscribe_from_events(self, subscriber_id: str):
        """Unsubscribe from event notifications"""
        if subscriber_id in self.subscribers:
            del self.subscribers[subscriber_id]
            logger.info(
                f"Subscriber {subscriber_id} unregistered from event notifications"
            )

    def add_custom_pattern(self, pattern: EventPattern):
        """Add custom event detection pattern"""
        self.event_patterns[pattern.pattern_id] = pattern
        logger.info(f"Added custom event pattern: {pattern.pattern_id}")

    def enable_pattern(self, pattern_id: str, enabled: bool = True):
        """Enable/disable an event pattern"""
        if pattern_id in self.event_patterns:
            self.event_patterns[pattern_id].enabled = enabled
            logger.info(f"Pattern {pattern_id} {'enabled' if enabled else 'disabled'}")

    def get_detection_metrics(self) -> Dict[str, Any]:
        """Get event detection metrics"""
        return self.detection_metrics.copy()

    def get_recent_events(
        self, hours: int = 24, severity: Optional[EventSeverity] = None
    ) -> List[BusinessEvent]:
        """Get recent events within specified time window"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        recent = []
        for events in self.recent_events.values():
            for event in events:
                if event.detection_date >= cutoff:
                    if not severity or event.severity == severity:
                        recent.append(event)

        return sorted(recent, key=lambda x: x.detection_date, reverse=True)
