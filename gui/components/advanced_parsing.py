"""
Advanced Data Parsing System with ML Models and Multi-format Support
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QGroupBox, QLabel, QPushButton, QComboBox, QCheckBox,
                            QTextEdit, QTabWidget, QTableWidget, QTableWidgetItem,
                            QProgressBar, QSlider, QSpinBox, QListWidget,
                            QFileDialog, QSplitter)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QTextCursor
import json
import csv
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
import io
import re
from pathlib import Path

# ML and NLP imports
try:
    import spacy
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    import pytesseract
    from PIL import Image
    import fitz  # PyMuPDF
    ADVANCED_PARSING_AVAILABLE = True
except ImportError:
    ADVANCED_PARSING_AVAILABLE = False

logger = logging.getLogger(__name__)

class ParsingMode(Enum):
    REALTIME = "realtime"
    BATCH = "batch"

class FileFormat(Enum):
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    HTML = "html"
    PDF = "pdf"
    IMAGE = "image"
    EXCEL = "excel"

@dataclass
class ParsingRule:
    """Custom parsing rule configuration"""
    name: str
    pattern: str
    extraction_type: str = "regex"  # regex, xpath, css, ml
    output_format: str = "text"
    preprocessing: List[str] = field(default_factory=list)
    postprocessing: List[str] = field(default_factory=list)
    confidence_threshold: float = 0.8
    enabled: bool = True

@dataclass
class MLModelConfig:
    """Machine learning model configuration"""
    model_name: str
    model_type: str  # spacy, transformers, custom
    task: str  # ner, classification, extraction, clustering
    parameters: Dict[str, Any] = field(default_factory=dict)
    cache_results: bool = True
    batch_size: int = 32

class AdvancedParser:
    """Advanced parsing engine with ML capabilities"""
    
    def __init__(self):
        self.nlp_models = {}
        self.transformers_models = {}
        self.custom_rules = []
        self.preprocessing_functions = {
            'lowercase': lambda x: x.lower(),
            'remove_html': lambda x: re.sub(r'<[^>]+>', '', x),
            'remove_urls': lambda x: re.sub(r'http\S+', '', x),
            'normalize_whitespace': lambda x: re.sub(r'\s+', ' ', x).strip(),
            'remove_punctuation': lambda x: re.sub(r'[^\w\s]', '', x)
        }
        
        if ADVANCED_PARSING_AVAILABLE:
            self.initialize_models()
            
    def initialize_models(self):
        """Initialize ML models"""
        try:
            # Load spaCy model
            self.nlp_models['default'] = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            
        try:
            # Load transformer models
            self.transformers_models['ner'] = pipeline("ner", aggregation_strategy="simple")
            self.transformers_models['classification'] = pipeline("text-classification")
            self.transformers_models['summarization'] = pipeline("summarization")
        except Exception as e:
            logger.warning(f"Failed to load transformer models: {e}")
            
    def parse_file(self, file_path: str, format_type: FileFormat, rules: List[ParsingRule]) -> Dict[str, Any]:
        """Parse file using specified format and rules"""
        try:
            if format_type == FileFormat.TEXT:
                return self._parse_text_file(file_path, rules)
            elif format_type == FileFormat.JSON:
                return self._parse_json_file(file_path, rules)
            elif format_type == FileFormat.XML:
                return self._parse_xml_file(file_path, rules)
            elif format_type == FileFormat.CSV:
                return self._parse_csv_file(file_path, rules)
            elif format_type == FileFormat.HTML:
                return self._parse_html_file(file_path, rules)
            elif format_type == FileFormat.PDF:
                return self._parse_pdf_file(file_path, rules)
            elif format_type == FileFormat.IMAGE:
                return self._parse_image_file(file_path, rules)
            else:
                return {"error": f"Unsupported format: {format_type}"}
                
        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            return {"error": str(e)}
            
    def _parse_text_file(self, file_path: str, rules: List[ParsingRule]) -> Dict[str, Any]:
        """Parse plain text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return self._apply_parsing_rules(content, rules)
        
    def _parse_json_file(self, file_path: str, rules: List[ParsingRule]) -> Dict[str, Any]:
        """Parse JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Convert to text for rule application
        content = json.dumps(data, indent=2)
        results = self._apply_parsing_rules(content, rules)
        results['structured_data'] = data
        return results
        
    def _parse_xml_file(self, file_path: str, rules: List[ParsingRule]) -> Dict[str, Any]:
        """Parse XML file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Convert to text
        content = ET.tostring(root, encoding='unicode')
        results = self._apply_parsing_rules(content, rules)
        
        # Add structured data
        results['xml_root'] = self._xml_to_dict(root)
        return results
        
    def _parse_csv_file(self, file_path: str, rules: List[ParsingRule]) -> Dict[str, Any]:
        """Parse CSV file"""
        df = pd.read_csv(file_path)
        
        # Convert to text for rule application
        content = df.to_string()
        results = self._apply_parsing_rules(content, rules)
        
        # Add structured data
        results['dataframe'] = df.to_dict('records')
        results['columns'] = list(df.columns)
        return results
        
    def _parse_html_file(self, file_path: str, rules: List[ParsingRule]) -> Dict[str, Any]:
        """Parse HTML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Remove HTML tags for text processing
        text_content = re.sub(r'<[^>]+>', ' ', content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        results = self._apply_parsing_rules(text_content, rules)
        results['raw_html'] = content
        return results
        
    def _parse_pdf_file(self, file_path: str, rules: List[ParsingRule]) -> Dict[str, Any]:
        """Parse PDF file using OCR"""
        if not ADVANCED_PARSING_AVAILABLE:
            return {"error": "Advanced parsing not available"}
            
        try:
            doc = fitz.open(file_path)
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()
                
            doc.close()
            
            results = self._apply_parsing_rules(text_content, rules)
            results['page_count'] = len(doc)
            return results
            
        except Exception as e:
            return {"error": f"PDF parsing failed: {e}"}
            
    def _parse_image_file(self, file_path: str, rules: List[ParsingRule]) -> Dict[str, Any]:
        """Parse image file using OCR"""
        if not ADVANCED_PARSING_AVAILABLE:
            return {"error": "OCR not available"}
            
        try:
            image = Image.open(file_path)
            text_content = pytesseract.image_to_string(image)
            
            results = self._apply_parsing_rules(text_content, rules)
            results['image_size'] = image.size
            return results
            
        except Exception as e:
            return {"error": f"Image OCR failed: {e}"}
            
    def _apply_parsing_rules(self, content: str, rules: List[ParsingRule]) -> Dict[str, Any]:
        """Apply parsing rules to content"""
        results = {
            'raw_content': content,
            'extracted_data': {},
            'entities': [],
            'classifications': [],
            'summary': None,
            'confidence_scores': {}
        }
        
        # Apply preprocessing
        processed_content = content
        for rule in rules:
            if not rule.enabled:
                continue
                
            for preprocess in rule.preprocessing:
                if preprocess in self.preprocessing_functions:
                    processed_content = self.preprocessing_functions[preprocess](processed_content)
                    
        # Apply extraction rules
        for rule in rules:
            if not rule.enabled:
                continue
                
            extracted = self._extract_by_rule(processed_content, rule)
            if extracted:
                results['extracted_data'][rule.name] = extracted
                
        # Apply ML models if available
        if ADVANCED_PARSING_AVAILABLE:
            results.update(self._apply_ml_models(processed_content))
            
        return results
        
    def _extract_by_rule(self, content: str, rule: ParsingRule) -> Any:
        """Extract data using specific rule"""
        try:
            if rule.extraction_type == "regex":
                matches = re.findall(rule.pattern, content, re.IGNORECASE | re.MULTILINE)
                return matches
                
            elif rule.extraction_type == "ml" and ADVANCED_PARSING_AVAILABLE:
                return self._ml_extraction(content, rule)
                
        except Exception as e:
            logger.error(f"Rule extraction failed for {rule.name}: {e}")
            
        return None
        
    def _ml_extraction(self, content: str, rule: ParsingRule) -> Any:
        """Machine learning based extraction"""
        try:
            if 'ner' in self.transformers_models:
                entities = self.transformers_models['ner'](content)
                return [entity for entity in entities if entity['score'] >= rule.confidence_threshold]
                
        except Exception as e:
            logger.error(f"ML extraction failed: {e}")
            
        return None
        
    def _apply_ml_models(self, content: str) -> Dict[str, Any]:
        """Apply ML models for advanced analysis"""
        ml_results = {}
        
        try:
            # Named Entity Recognition
            if 'ner' in self.transformers_models:
                entities = self.transformers_models['ner'](content)
                ml_results['entities'] = entities
                
            # Text Classification
            if 'classification' in self.transformers_models:
                classification = self.transformers_models['classification'](content)
                ml_results['classification'] = classification
                
            # Text Summarization (for long texts)
            if 'summarization' in self.transformers_models and len(content) > 1000:
                try:
                    summary = self.transformers_models['summarization'](
                        content[:1024], max_length=150, min_length=50
                    )
                    ml_results['summary'] = summary[0]['summary_text']
                except Exception as e:
                    logger.warning(f"Summarization failed: {e}")
                    
            # spaCy processing
            if 'default' in self.nlp_models:
                doc = self.nlp_models['default'](content)
                ml_results['spacy_entities'] = [
                    {'text': ent.text, 'label': ent.label_, 'start': ent.start_char, 'end': ent.end_char}
                    for ent in doc.ents
                ]
                
        except Exception as e:
            logger.error(f"ML model application failed: {e}")
            
        return ml_results
        
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary"""
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
            
        # Add text content
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
            
        # Add child elements
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
                
        return result

class BatchProcessor(QThread):
    """Batch processing thread"""
    
    progress_updated = pyqtSignal(int, str)
    file_processed = pyqtSignal(str, dict)
    processing_completed = pyqtSignal(int, int)  # total, successful
    
    def __init__(self, files: List[str], rules: List[ParsingRule], parser: AdvancedParser):
        super().__init__()
        self.files = files
        self.rules = rules
        self.parser = parser
        self.running = True
        
    def run(self):
        """Process files in batch"""
        total_files = len(self.files)
        successful = 0
        
        for i, file_path in enumerate(self.files):
            if not self.running:
                break
                
            self.progress_updated.emit(int((i / total_files) * 100), f"Processing {Path(file_path).name}")
            
            try:
                # Detect file format
                file_format = self._detect_format(file_path)
                
                # Process file
                results = self.parser.parse_file(file_path, file_format, self.rules)
                
                if 'error' not in results:
                    successful += 1
                    
                self.file_processed.emit(file_path, results)
                
            except Exception as e:
                logger.error(f"Batch processing failed for {file_path}: {e}")
                self.file_processed.emit(file_path, {"error": str(e)})
                
        self.processing_completed.emit(total_files, successful)
        
    def stop(self):
        """Stop batch processing"""
        self.running = False
        
    def _detect_format(self, file_path: str) -> FileFormat:
        """Auto-detect file format"""
        extension = Path(file_path).suffix.lower()
        
        format_map = {
            '.txt': FileFormat.TEXT,
            '.json': FileFormat.JSON,
            '.xml': FileFormat.XML,
            '.csv': FileFormat.CSV,
            '.html': FileFormat.HTML,
            '.htm': FileFormat.HTML,
            '.pdf': FileFormat.PDF,
            '.png': FileFormat.IMAGE,
            '.jpg': FileFormat.IMAGE,
            '.jpeg': FileFormat.IMAGE,
            '.xlsx': FileFormat.EXCEL,
            '.xls': FileFormat.EXCEL
        }
        
        return format_map.get(extension, FileFormat.TEXT)

class ParsingWidget(QWidget):
    """Advanced data parsing configuration widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parser = AdvancedParser()
        self.parsing_rules = []
        self.batch_processor = None
        self.processed_results = {}
        
        self.setup_ui()
        self.connect_signals()
        self.load_default_rules()
        
    def setup_ui(self):
        """Setup parsing widget UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Rules configuration tab
        self.rules_tab = self.create_rules_tab()
        self.tab_widget.addTab(self.rules_tab, "Parsing Rules")
        
        # ML models tab
        self.models_tab = self.create_models_tab()
        self.tab_widget.addTab(self.models_tab, "ML Models")
        
        # Batch processing tab
        self.batch_tab = self.create_batch_tab()
        self.tab_widget.addTab(self.batch_tab, "Batch Processing")
        
        # Results tab
        self.results_tab = self.create_results_tab()
        self.tab_widget.addTab(self.results_tab, "Results")
        
        layout.addWidget(self.tab_widget)
        
    def create_rules_tab(self) -> QWidget:
        """Create parsing rules configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Rule controls
        controls_layout = QHBoxLayout()
        
        self.add_rule_btn = QPushButton("Add Rule")
        self.remove_rule_btn = QPushButton("Remove Rule")
        self.test_rule_btn = QPushButton("Test Rule")
        
        controls_layout.addWidget(self.add_rule_btn)
        controls_layout.addWidget(self.remove_rule_btn)
        controls_layout.addWidget(self.test_rule_btn)
        controls_layout.addStretch()
        
        # Rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(6)
        self.rules_table.setHorizontalHeaderLabels([
            "Name", "Pattern", "Type", "Confidence", "Enabled", "Actions"
        ])
        
        # Rule editor
        editor_group = QGroupBox("Rule Editor")
        editor_layout = QGridLayout(editor_group)
        
        editor_layout.addWidget(QLabel("Name:"), 0, 0)
        self.rule_name_edit = QLineEdit()
        editor_layout.addWidget(self.rule_name_edit, 0, 1)
        
        editor_layout.addWidget(QLabel("Pattern:"), 1, 0)
        self.rule_pattern_edit = QTextEdit()
        self.rule_pattern_edit.setMaximumHeight(100)
        editor_layout.addWidget(self.rule_pattern_edit, 1, 1)
        
        editor_layout.addWidget(QLabel("Type:"), 2, 0)
        self.rule_type_combo = QComboBox()
        self.rule_type_combo.addItems(["regex", "xpath", "css", "ml"])
        editor_layout.addWidget(self.rule_type_combo, 2, 1)
        
        editor_layout.addWidget(QLabel("Confidence:"), 3, 0)
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(80)
        self.confidence_label = QLabel("0.80")
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(self.confidence_slider)
        conf_layout.addWidget(self.confidence_label)
        editor_layout.addLayout(conf_layout, 3, 1)
        
        # Test area
        test_group = QGroupBox("Rule Testing")
        test_layout = QVBoxLayout(test_group)
        
        self.test_input = QTextEdit()
        self.test_input.setPlaceholderText("Enter test text here...")
        self.test_input.setMaximumHeight(100)
        
        self.test_output = QTextEdit()
        self.test_output.setReadOnly(True)
        self.test_output.setMaximumHeight(100)
        
        test_layout.addWidget(QLabel("Test Input:"))
        test_layout.addWidget(self.test_input)
        test_layout.addWidget(QLabel("Test Output:"))
        test_layout.addWidget(self.test_output)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.rules_table)
        layout.addWidget(editor_group)
        layout.addWidget(test_group)
        
        return widget
        
    def create_models_tab(self) -> QWidget:
        """Create ML models configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Model status
        status_group = QGroupBox("Model Status")
        status_layout = QGridLayout(status_group)
        
        self.spacy_status = QLabel("❌ Not Available")
        self.transformers_status = QLabel("❌ Not Available")
        self.ocr_status = QLabel("❌ Not Available")
        
        status_layout.addWidget(QLabel("spaCy:"), 0, 0)
        status_layout.addWidget(self.spacy_status, 0, 1)
        
        status_layout.addWidget(QLabel("Transformers:"), 1, 0)
        status_layout.addWidget(self.transformers_status, 1, 1)
        
        status_layout.addWidget(QLabel("OCR (Tesseract):"), 2, 0)
        status_layout.addWidget(self.ocr_status, 2, 1)
        
        # Model configuration
        config_group = QGroupBox("Model Configuration")
        config_layout = QGridLayout(config_group)
        
        config_layout.addWidget(QLabel("spaCy Model:"), 0, 0)
        self.spacy_model_combo = QComboBox()
        self.spacy_model_combo.addItems(["en_core_web_sm", "en_core_web_md", "en_core_web_lg"])
        config_layout.addWidget(self.spacy_model_combo, 0, 1)
        
        config_layout.addWidget(QLabel("Batch Size:"), 1, 0)
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 128)
        self.batch_size_spin.setValue(32)
        config_layout.addWidget(self.batch_size_spin, 1, 1)
        
        self.cache_results_cb = QCheckBox("Cache Results")
        self.cache_results_cb.setChecked(True)
        config_layout.addWidget(self.cache_results_cb, 2, 0, 1, 2)
        
        layout.addWidget(status_group)
        layout.addWidget(config_group)
        layout.addStretch()
        
        # Update status
        self.update_model_status()
        
        return widget
        
    def create_batch_tab(self) -> QWidget:
        """Create batch processing tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File selection
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        file_controls = QHBoxLayout()
        self.add_files_btn = QPushButton("Add Files")
        self.add_folder_btn = QPushButton("Add Folder")
        self.clear_files_btn = QPushButton("Clear Files")
        
        file_controls.addWidget(self.add_files_btn)
        file_controls.addWidget(self.add_folder_btn)
        file_controls.addWidget(self.clear_files_btn)
        file_controls.addStretch()
        
        self.files_list = QListWidget()
        
        file_layout.addLayout(file_controls)
        file_layout.addWidget(self.files_list)
        
        # Processing controls
        processing_group = QGroupBox("Processing")
        processing_layout = QVBoxLayout(processing_group)
        
        proc_controls = QHBoxLayout()
        self.start_batch_btn = QPushButton("Start Batch")
        self.stop_batch_btn = QPushButton("Stop Batch")
        self.stop_batch_btn.setEnabled(False)
        
        proc_controls.addWidget(self.start_batch_btn)
        proc_controls.addWidget(self.stop_batch_btn)
        proc_controls.addStretch()
        
        self.batch_progress = QProgressBar()
        self.batch_status = QLabel("Ready")
        
        processing_layout.addLayout(proc_controls)
        processing_layout.addWidget(self.batch_progress)
        processing_layout.addWidget(self.batch_status)
        
        layout.addWidget(file_group)
        layout.addWidget(processing_group)
        
        return widget
        
    def create_results_tab(self) -> QWidget:
        """Create results display tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Results controls
        controls_layout = QHBoxLayout()
        
        self.export_results_btn = QPushButton("Export Results")
        self.clear_results_btn = QPushButton("Clear Results")
        
        controls_layout.addWidget(self.export_results_btn)
        controls_layout.addWidget(self.clear_results_btn)
        controls_layout.addStretch()
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier", 9))
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.results_text)
        
        return widget
        
    def connect_signals(self):
        """Connect UI signals"""
        # Rules tab
        self.add_rule_btn.clicked.connect(self.add_parsing_rule)
        self.remove_rule_btn.clicked.connect(self.remove_parsing_rule)
        self.test_rule_btn.clicked.connect(self.test_parsing_rule)
        self.confidence_slider.valueChanged.connect(self.update_confidence_label)
        
        # Batch tab
        self.add_files_btn.clicked.connect(self.add_files)
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.clear_files_btn.clicked.connect(self.clear_files)
        self.start_batch_btn.clicked.connect(self.start_batch_processing)
        self.stop_batch_btn.clicked.connect(self.stop_batch_processing)
        
        # Results tab
        self.export_results_btn.clicked.connect(self.export_results)
        self.clear_results_btn.clicked.connect(self.clear_results)
        
    def update_model_status(self):
        """Update ML model availability status"""
        if ADVANCED_PARSING_AVAILABLE:
            if 'default' in self.parser.nlp_models:
                self.spacy_status.setText("✅ Available")
            if self.parser.transformers_models:
                self.transformers_status.setText("✅ Available")
            try:
                import pytesseract
                self.ocr_status.setText("✅ Available")
            except ImportError:
                pass
                
    def update_confidence_label(self, value):
        """Update confidence threshold label"""
        self.confidence_label.setText(f"{value/100:.2f}")
        
    def load_default_rules(self):
        """Load default parsing rules"""
        default_rules = [
            ParsingRule("Email Addresses", r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            ParsingRule("Phone Numbers", r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            ParsingRule("URLs", r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            ParsingRule("Dates", r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),
            ParsingRule("Credit Cards", r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
        ]
        
        self.parsing_rules.extend(default_rules)
        self.refresh_rules_table()
        
    def add_parsing_rule(self):
        """Add new parsing rule"""
        name = self.rule_name_edit.text() or f"Rule {len(self.parsing_rules) + 1}"
        pattern = self.rule_pattern_edit.toPlainText()
        rule_type = self.rule_type_combo.currentText()
        confidence = self.confidence_slider.value() / 100
        
        if pattern:
            rule = ParsingRule(
                name=name,
                pattern=pattern,
                extraction_type=rule_type,
                confidence_threshold=confidence
            )
            self.parsing_rules.append(rule)
            self.refresh_rules_table()
            
            # Clear form
            self.rule_name_edit.clear()
            self.rule_pattern_edit.clear()
            
    def remove_parsing_rule(self):
        """Remove selected parsing rule"""
        current_row = self.rules_table.currentRow()
        if current_row >= 0:
            del self.parsing_rules[current_row]
            self.refresh_rules_table()
            
    def test_parsing_rule(self):
        """Test current parsing rule"""
        pattern = self.rule_pattern_edit.toPlainText()
        test_text = self.test_input.toPlainText()
        
        if pattern and test_text:
            try:
                matches = re.findall(pattern, test_text, re.IGNORECASE | re.MULTILINE)
                self.test_output.setText(f"Matches found: {len(matches)}\n\n" + "\n".join(str(match) for match in matches))
            except Exception as e:
                self.test_output.setText(f"Error: {str(e)}")
                
    def refresh_rules_table(self):
        """Refresh parsing rules table"""
        self.rules_table.setRowCount(len(self.parsing_rules))
        
        for row, rule in enumerate(self.parsing_rules):
            self.rules_table.setItem(row, 0, QTableWidgetItem(rule.name))
            self.rules_table.setItem(row, 1, QTableWidgetItem(rule.pattern[:50] + "..."))
            self.rules_table.setItem(row, 2, QTableWidgetItem(rule.extraction_type))
            self.rules_table.setItem(row, 3, QTableWidgetItem(f"{rule.confidence_threshold:.2f}"))
            
            enabled_cb = QCheckBox()
            enabled_cb.setChecked(rule.enabled)
            enabled_cb.stateChanged.connect(lambda state, r=row: self.toggle_rule_enabled(r, state))
            self.rules_table.setCellWidget(row, 4, enabled_cb)
            
    def toggle_rule_enabled(self, row: int, state: int):
        """Toggle rule enabled state"""
        if 0 <= row < len(self.parsing_rules):
            self.parsing_rules[row].enabled = state == Qt.CheckState.Checked.value
            
    def add_files(self):
        """Add files for batch processing"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files for Batch Processing",
            "",
            "All Files (*);;Text Files (*.txt);;JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        for file_path in files:
            self.files_list.addItem(file_path)
            
    def add_folder(self):
        """Add folder for batch processing"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder:
            folder_path = Path(folder)
            for file_path in folder_path.rglob("*"):
                if file_path.is_file():
                    self.files_list.addItem(str(file_path))
                    
    def clear_files(self):
        """Clear files list"""
        self.files_list.clear()
        
    def start_batch_processing(self):
        """Start batch processing"""
        files = [self.files_list.item(i).text() for i in range(self.files_list.count())]
        
        if not files:
            return
            
        self.batch_processor = BatchProcessor(files, self.parsing_rules, self.parser)
        self.batch_processor.progress_updated.connect(self.update_batch_progress)
        self.batch_processor.file_processed.connect(self.add_batch_result)
        self.batch_processor.processing_completed.connect(self.batch_processing_completed)
        
        self.start_batch_btn.setEnabled(False)
        self.stop_batch_btn.setEnabled(True)
        self.batch_progress.setValue(0)
        
        self.batch_processor.start()
        
    def stop_batch_processing(self):
        """Stop batch processing"""
        if self.batch_processor:
            self.batch_processor.stop()
            
    def update_batch_progress(self, progress: int, status: str):
        """Update batch processing progress"""
        self.batch_progress.setValue(progress)
        self.batch_status.setText(status)
        
    def add_batch_result(self, file_path: str, results: Dict[str, Any]):
        """Add batch processing result"""
        self.processed_results[file_path] = results
        
        # Update results display
        result_summary = f"\n=== {Path(file_path).name} ===\n"
        
        if 'error' in results:
            result_summary += f"Error: {results['error']}\n"
        else:
            result_summary += f"Extracted data points: {len(results.get('extracted_data', {}))}\n"
            result_summary += f"Entities found: {len(results.get('entities', []))}\n"
            
        current_text = self.results_text.toPlainText()
        self.results_text.setText(current_text + result_summary)
        
        # Scroll to bottom
        cursor = self.results_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.results_text.setTextCursor(cursor)
        
    def batch_processing_completed(self, total: int, successful: int):
        """Handle batch processing completion"""
        self.start_batch_btn.setEnabled(True)
        self.stop_batch_btn.setEnabled(False)
        self.batch_status.setText(f"Completed: {successful}/{total} files processed successfully")
        
    def export_results(self):
        """Export processing results"""
        if not self.processed_results:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "parsing_results.json",
            "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if file_path:
            if file_path.endswith('.json'):
                with open(file_path, 'w') as f:
                    json.dump(self.processed_results, f, indent=2, default=str)
            elif file_path.endswith('.csv'):
                # Flatten results for CSV export
                flattened_data = []
                for file, results in self.processed_results.items():
                    row = {'file': file}
                    if 'extracted_data' in results:
                        for key, value in results['extracted_data'].items():
                            row[f'extracted_{key}'] = str(value)
                    flattened_data.append(row)
                    
                df = pd.DataFrame(flattened_data)
                df.to_csv(file_path, index=False)
                
    def clear_results(self):
        """Clear all results"""
        self.processed_results.clear()
        self.results_text.clear()
        self.batch_progress.setValue(0)
        self.batch_status.setText("Ready")
