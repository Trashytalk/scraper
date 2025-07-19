"""
Interactive Tooltip System with Context Awareness and Experience Levels
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QEvent, QPoint, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QEnterEvent, QPixmap
from PyQt6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class ExperienceLevel:
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TooltipContent:
    def __init__(
        self,
        text: str,
        level: str = ExperienceLevel.BEGINNER,
        media_path: Optional[str] = None,
        context_tags: Optional[List[str]] = None,
    ) -> None:
        self.text = text
        self.level = level
        self.media_path = media_path
        self.context_tags = context_tags or []


class InteractiveTooltip(QFrame):
    """Enhanced tooltip with media support and experience levels"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent, Qt.WindowType.ToolTip)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(
            """
            QFrame {
                background-color: rgba(45, 45, 48, 240);
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 8px;
                color: white;
            }
        """
        )

        self.main_layout = QVBoxLayout(self)
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setMaximumWidth(400)

        self.media_label = QLabel()
        self.media_label.setVisible(False)

        self.level_indicator = QLabel()
        self.level_indicator.setStyleSheet("color: #00ff88; font-size: 10px;")

        self.main_layout.addWidget(self.level_indicator)
        self.main_layout.addWidget(self.text_label)
        self.main_layout.addWidget(self.media_label)

    def set_content(self, content: TooltipContent) -> None:
        """Set tooltip content with experience level context"""
        self.text_label.setText(content.text)
        self.level_indicator.setText(f"Level: {content.level.title()}")

        # Add media support for images and videos
        if content.media_path:
            self.load_media(content.media_path)
            self.media_label.setVisible(True)
        else:
            self.media_label.setVisible(False)

        self.adjustSize()

    def load_media(self, media_path: str) -> None:
        """Load and display media content"""
        try:
            file_path = Path(media_path)

            if file_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
                # Load image
                pixmap = QPixmap(media_path)
                if not pixmap.isNull():
                    # Scale image to fit tooltip
                    scaled_pixmap = pixmap.scaled(
                        200,
                        150,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    self.media_label.setPixmap(scaled_pixmap)
                else:
                    self.media_label.setText(f"Image: {file_path.name}")

            elif file_path.suffix.lower() in [".mp4", ".avi", ".mov", ".wmv"]:
                # Video placeholder - future implementation
                self.media_label.setText(f"🎥 Video: {file_path.name}")

            else:
                self.media_label.setText(f"Media: {file_path.name}")

        except Exception as e:
            logger.error(f"Failed to load media {media_path}: {e}")
            self.media_label.setText(f"Media: {Path(media_path).name}")


class TooltipManager:
    """Manages context-aware tooltips across the application"""

    def __init__(self) -> None:
        self.experience_level = ExperienceLevel.BEGINNER
        self.tooltip_definitions: Dict[str, Dict[str, TooltipContent]] = {}
        self.active_tooltip: Optional[InteractiveTooltip] = None
        self.context_cache: Dict[str, Any] = {}

        # Load tooltip definitions
        self.load_tooltip_definitions()

    def set_experience_level(self, level: str) -> None:
        """Set user experience level for tooltip content"""
        self.experience_level = level
        logger.info(f"Experience level set to: {level}")

    def load_tooltip_definitions(self) -> None:
        """Load tooltip definitions from configuration"""
        # Define default tooltips for different experience levels
        self.tooltip_definitions = {
            "spider_config": {
                ExperienceLevel.BEGINNER: TooltipContent(
                    "Spiders are programs that automatically browse websites to collect information. Click here to configure how your spider behaves.",
                    ExperienceLevel.BEGINNER,
                ),
                ExperienceLevel.INTERMEDIATE: TooltipContent(
                    "Configure spider parameters including request headers, delays, concurrent requests, and retry policies for optimal scraping performance.",
                    ExperienceLevel.INTERMEDIATE,
                ),
                ExperienceLevel.ADVANCED: TooltipContent(
                    "Advanced spider configuration: middleware stack, download handlers, item pipelines, custom extensions, and per-domain settings.",
                    ExperienceLevel.ADVANCED,
                ),
                ExperienceLevel.EXPERT: TooltipContent(
                    "Full spider customization with reactor settings, DNS resolver configuration, HTTP/2 support, and distributed crawling parameters.",
                    ExperienceLevel.EXPERT,
                ),
            },
            "proxy_rotation": {
                ExperienceLevel.BEGINNER: TooltipContent(
                    "Proxy rotation helps hide your identity by changing your IP address automatically. This prevents websites from blocking you.",
                    ExperienceLevel.BEGINNER,
                ),
                ExperienceLevel.INTERMEDIATE: TooltipContent(
                    "Configure proxy pools, rotation strategies, health checking, and failover mechanisms for reliable anonymous scraping.",
                    ExperienceLevel.INTERMEDIATE,
                ),
                ExperienceLevel.ADVANCED: TooltipContent(
                    "Advanced proxy management with sticky sessions, geolocation targeting, provider-specific optimizations, and custom authentication.",
                    ExperienceLevel.ADVANCED,
                ),
                ExperienceLevel.EXPERT: TooltipContent(
                    "Enterprise proxy configuration with load balancing algorithms, circuit breakers, performance analytics, and dynamic pool management.",
                    ExperienceLevel.EXPERT,
                ),
            },
            "job_management": {
                ExperienceLevel.BEGINNER: TooltipContent(
                    "Jobs are scraping tasks that run automatically. You can start, stop, and monitor your scraping jobs here.",
                    ExperienceLevel.BEGINNER,
                ),
                ExperienceLevel.INTERMEDIATE: TooltipContent(
                    "Manage scraping jobs with scheduling, priority queues, resource allocation, and automatic retry mechanisms.",
                    ExperienceLevel.INTERMEDIATE,
                ),
                ExperienceLevel.ADVANCED: TooltipContent(
                    "Advanced job orchestration with dependency management, parallel execution, custom hooks, and distributed processing.",
                    ExperienceLevel.ADVANCED,
                ),
                ExperienceLevel.EXPERT: TooltipContent(
                    "Enterprise job management with cluster coordination, auto-scaling, performance optimization, and failure recovery.",
                    ExperienceLevel.EXPERT,
                ),
            },
            "data_export": {
                ExperienceLevel.BEGINNER: TooltipContent(
                    "Export your scraped data to files like CSV or JSON. Choose the format that works best for your needs.",
                    ExperienceLevel.BEGINNER,
                ),
                ExperienceLevel.INTERMEDIATE: TooltipContent(
                    "Export data with custom formatting, filtering, and transformation options. Supports multiple output formats and destinations.",
                    ExperienceLevel.INTERMEDIATE,
                ),
                ExperienceLevel.ADVANCED: TooltipContent(
                    "Advanced export with data pipelines, real-time streaming, custom serializers, and integration with external systems.",
                    ExperienceLevel.ADVANCED,
                ),
                ExperienceLevel.EXPERT: TooltipContent(
                    "Enterprise data export with ETL pipelines, data validation, schema evolution, and high-performance streaming to multiple destinations.",
                    ExperienceLevel.EXPERT,
                ),
            },
            "performance_metrics": {
                ExperienceLevel.BEGINNER: TooltipContent(
                    "See how fast your scraping is working and if there are any problems. Green means good, red means issues.",
                    ExperienceLevel.BEGINNER,
                ),
                ExperienceLevel.INTERMEDIATE: TooltipContent(
                    "Monitor scraping performance with request rates, response times, error rates, and resource utilization metrics.",
                    ExperienceLevel.INTERMEDIATE,
                ),
                ExperienceLevel.ADVANCED: TooltipContent(
                    "Advanced performance analytics with custom metrics, alerting, profiling, and optimization recommendations.",
                    ExperienceLevel.ADVANCED,
                ),
                ExperienceLevel.EXPERT: TooltipContent(
                    "Enterprise monitoring with distributed tracing, custom dashboards, predictive analytics, and automated performance tuning.",
                    ExperienceLevel.EXPERT,
                ),
            },
            # Add more tooltip definitions...
        }

    def get_tooltip_content(
        self, tooltip_id: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[TooltipContent]:
        """Get context-aware tooltip content based on experience level"""
        if tooltip_id not in self.tooltip_definitions:
            return None

        level_content = self.tooltip_definitions[tooltip_id]

        # Get content for current experience level or fallback
        content: Optional[TooltipContent] = level_content.get(self.experience_level)
        if not content and self.experience_level != ExperienceLevel.BEGINNER:
            content = level_content.get(ExperienceLevel.BEGINNER)

        return content

    def show_tooltip(
        self, widget: QWidget, tooltip_id: str, position: Optional[QPoint] = None
    ) -> None:
        """Show interactive tooltip for widget"""
        content = self.get_tooltip_content(tooltip_id)
        if not content:
            return

        if self.active_tooltip:
            self.active_tooltip.hide()

        self.active_tooltip = InteractiveTooltip(widget)
        self.active_tooltip.set_content(content)

        if position is not None:
            self.active_tooltip.move(position)
        else:
            self.active_tooltip.move(widget.mapToGlobal(widget.rect().bottomLeft()))

        self.active_tooltip.show()

        # Auto-hide after delay
        QTimer.singleShot(5000, self.hide_tooltip)

    def hide_tooltip(self) -> None:
        """Hide active tooltip"""
        if self.active_tooltip:
            self.active_tooltip.hide()
            self.active_tooltip = None


# Global tooltip manager instance
tooltip_manager = TooltipManager()


class TooltipWidget(QWidget):
    """Base widget class with tooltip support"""

    def __init__(self, tooltip_id: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.tooltip_id = tooltip_id
        self.setMouseTracking(True)

    def enterEvent(self, event: Optional[QEnterEvent]) -> None:
        """Show tooltip on mouse enter"""
        tooltip_manager.show_tooltip(self, self.tooltip_id)
        super().enterEvent(event)

    def leaveEvent(self, event: Optional[QEvent]) -> None:
        """Hide tooltip on mouse leave"""
        tooltip_manager.hide_tooltip()
        super().leaveEvent(event)


class ExperienceLevelSelector(QWidget):
    """Widget for selecting user experience level"""

    level_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QHBoxLayout(self)

        label = QLabel("Experience Level:")
        self.combo = QComboBox()
        self.combo.addItems(["Beginner", "Intermediate", "Advanced", "Expert"])

        self.combo.currentTextChanged.connect(self.on_level_changed)

        layout.addWidget(label)
        layout.addWidget(self.combo)

    def on_level_changed(self, text: str) -> None:
        """Handle experience level change"""
        level = text.lower()
        tooltip_manager.set_experience_level(level)
        self.level_changed.emit(level)
