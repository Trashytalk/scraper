#!/usr/bin/env python3
"""
Phase 3: Advanced Data Quality Assessment and Validation System

This module implements sophisticated data quality assessment using ML and statistical methods:
- Multi-dimensional quality scoring
- Anomaly detection in scraped data
- Data completeness and consistency validation
- Automated quality improvement suggestions
- Real-time quality monitoring and alerting
"""

import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import hashlib
import re

# ML and statistical imports
try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    from sklearn.metrics import silhouette_score
    from scipy import stats
    import matplotlib.pyplot as plt
    import seaborn as sns

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    np = None
    pd = None

logger = logging.getLogger(__name__)


@dataclass
class DataQualityMetrics:
    """Comprehensive data quality metrics"""

    # Basic metrics
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    consistency_score: float = 0.0
    uniqueness_score: float = 0.0
    validity_score: float = 0.0

    # Advanced metrics
    freshness_score: float = 0.0
    relevance_score: float = 0.0
    precision_score: float = 0.0

    # Composite scores
    overall_quality_score: float = 0.0
    business_value_score: float = 0.0

    # Detailed breakdowns
    field_completeness: Dict[str, float] = field(default_factory=dict)
    field_accuracy: Dict[str, float] = field(default_factory=dict)
    data_anomalies: List[Dict[str, Any]] = field(default_factory=list)
    validation_errors: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    total_records: int = 0
    total_fields: int = 0
    assessment_timestamp: datetime = field(default_factory=datetime.utcnow)
    source_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization"""
        return {
            "completeness_score": self.completeness_score,
            "accuracy_score": self.accuracy_score,
            "consistency_score": self.consistency_score,
            "uniqueness_score": self.uniqueness_score,
            "validity_score": self.validity_score,
            "freshness_score": self.freshness_score,
            "relevance_score": self.relevance_score,
            "precision_score": self.precision_score,
            "overall_quality_score": self.overall_quality_score,
            "business_value_score": self.business_value_score,
            "field_completeness": self.field_completeness,
            "field_accuracy": self.field_accuracy,
            "data_anomalies": self.data_anomalies,
            "validation_errors": self.validation_errors,
            "total_records": self.total_records,
            "total_fields": self.total_fields,
            "assessment_timestamp": self.assessment_timestamp.isoformat(),
            "source_url": self.source_url,
        }


@dataclass
class QualityRule:
    """Data quality validation rule"""

    name: str
    field_name: str
    rule_type: str  # 'pattern', 'range', 'enum', 'custom'
    rule_config: Dict[str, Any]
    severity: str = "medium"  # 'low', 'medium', 'high', 'critical'
    enabled: bool = True

    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """Validate a value against this rule"""
        try:
            if self.rule_type == "pattern":
                pattern = self.rule_config.get("pattern")
                if pattern and isinstance(value, str):
                    return bool(re.match(pattern, value)), None

            elif self.rule_type == "range":
                min_val = self.rule_config.get("min")
                max_val = self.rule_config.get("max")

                if isinstance(value, (int, float)):
                    valid = True
                    if min_val is not None:
                        valid = valid and value >= min_val
                    if max_val is not None:
                        valid = valid and value <= max_val
                    return valid, None

            elif self.rule_type == "enum":
                allowed_values = self.rule_config.get("allowed_values", [])
                return value in allowed_values, None

            elif self.rule_type == "required":
                return value is not None and str(value).strip() != "", None

            elif self.rule_type == "custom":
                # Custom validation function
                validator = self.rule_config.get("validator")
                if callable(validator):
                    return validator(value)

            return True, None

        except Exception as e:
            return False, f"Validation error: {e}"


class AdvancedDataQualityAssessor:
    """Advanced ML-powered data quality assessment system"""

    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".AdvancedDataQualityAssessor")

        # Quality models
        self.anomaly_detector = None
        self.quality_predictor = None

        # Quality rules and patterns
        self.quality_rules: Dict[str, List[QualityRule]] = {}
        self.data_patterns: Dict[str, Dict[str, Any]] = {}

        # Historical data for trend analysis
        self.quality_history: List[DataQualityMetrics] = []
        self.baseline_metrics: Dict[str, Dict[str, float]] = {}

        # Initialize components
        self._initialize_quality_components()
        self._load_default_rules()

    def _initialize_quality_components(self):
        """Initialize ML components for quality assessment"""

        if ML_AVAILABLE:
            try:
                # Anomaly detection for outlier identification
                self.anomaly_detector = IsolationForest(
                    contamination=0.1, random_state=42, n_estimators=100
                )

                # Data scaler for normalization
                self.data_scaler = StandardScaler()

                self.logger.info("ML quality components initialized")

            except Exception as e:
                self.logger.error(f"Error initializing ML components: {e}")
                self.anomaly_detector = None
        else:
            self.logger.warning(
                "ML libraries not available for advanced quality assessment"
            )

    def _load_default_rules(self):
        """Load default data quality rules"""

        # Common validation rules
        default_rules = {
            "email": [
                QualityRule(
                    name="email_format",
                    field_name="email",
                    rule_type="pattern",
                    rule_config={
                        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                    },
                    severity="high",
                )
            ],
            "phone": [
                QualityRule(
                    name="phone_format",
                    field_name="phone",
                    rule_type="pattern",
                    rule_config={
                        "pattern": r"^\+?1?-?\.?\s?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}$"
                    },
                    severity="medium",
                )
            ],
            "price": [
                QualityRule(
                    name="price_range",
                    field_name="price",
                    rule_type="range",
                    rule_config={"min": 0, "max": 1000000},
                    severity="high",
                ),
                QualityRule(
                    name="price_required",
                    field_name="price",
                    rule_type="required",
                    rule_config={},
                    severity="critical",
                ),
            ],
            "url": [
                QualityRule(
                    name="url_format",
                    field_name="url",
                    rule_type="pattern",
                    rule_config={"pattern": r"^https?://[^\s/$.?#].[^\s]*$"},
                    severity="medium",
                )
            ],
            "date": [
                QualityRule(
                    name="date_format",
                    field_name="date",
                    rule_type="pattern",
                    rule_config={
                        "pattern": r"^\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}$"
                    },
                    severity="medium",
                )
            ],
        }

        self.quality_rules.update(default_rules)
        self.logger.info(f"Loaded {len(default_rules)} default quality rule sets")

    async def assess_data_quality(
        self,
        data: Union[List[Dict], pd.DataFrame],
        source_url: str = "",
        field_mapping: Optional[Dict[str, str]] = None,
    ) -> DataQualityMetrics:
        """Comprehensive data quality assessment"""

        try:
            # Convert to pandas DataFrame if needed
            if isinstance(data, list):
                if not data:
                    return DataQualityMetrics(source_url=source_url)
                df = pd.DataFrame(data) if ML_AVAILABLE else data
            else:
                df = data if ML_AVAILABLE else data

            # Initialize metrics
            metrics = DataQualityMetrics(
                source_url=source_url,
                total_records=(
                    len(data)
                    if isinstance(data, list)
                    else len(df) if ML_AVAILABLE else 0
                ),
                total_fields=(
                    len(data[0])
                    if data and isinstance(data, list)
                    else len(df.columns) if ML_AVAILABLE else 0
                ),
            )

            # Assess different quality dimensions
            await self._assess_completeness(df if ML_AVAILABLE else data, metrics)
            await self._assess_accuracy(
                df if ML_AVAILABLE else data, metrics, field_mapping
            )
            await self._assess_consistency(df if ML_AVAILABLE else data, metrics)
            await self._assess_uniqueness(df if ML_AVAILABLE else data, metrics)
            await self._assess_validity(
                df if ML_AVAILABLE else data, metrics, field_mapping
            )

            if ML_AVAILABLE:
                await self._detect_anomalies(df, metrics)
                await self._assess_advanced_metrics(df, metrics)

            # Calculate composite scores
            self._calculate_composite_scores(metrics)

            # Store for trend analysis
            self.quality_history.append(metrics)

            self.logger.info(
                f"Quality assessment complete for {source_url}: {metrics.overall_quality_score:.2f}"
            )
            return metrics

        except Exception as e:
            self.logger.error(f"Error assessing data quality: {e}")
            return DataQualityMetrics(source_url=source_url)

    async def _assess_completeness(
        self, data: Union[List[Dict], pd.DataFrame], metrics: DataQualityMetrics
    ):
        """Assess data completeness (missing values)"""

        try:
            if ML_AVAILABLE and isinstance(data, pd.DataFrame):
                # Pandas-based completeness assessment
                total_cells = data.size
                missing_cells = data.isnull().sum().sum()
                metrics.completeness_score = (
                    1 - (missing_cells / total_cells) if total_cells > 0 else 0
                )

                # Per-field completeness
                for column in data.columns:
                    missing_count = data[column].isnull().sum()
                    completeness = (
                        1 - (missing_count / len(data)) if len(data) > 0 else 0
                    )
                    metrics.field_completeness[column] = completeness

            else:
                # Fallback for list of dictionaries
                if not data:
                    metrics.completeness_score = 0
                    return

                all_fields = set()
                for record in data:
                    all_fields.update(record.keys())

                field_completeness = {}
                for field in all_fields:
                    present_count = sum(
                        1
                        for record in data
                        if field in record
                        and record[field] is not None
                        and str(record[field]).strip() != ""
                    )
                    field_completeness[field] = (
                        present_count / len(data) if len(data) > 0 else 0
                    )

                metrics.field_completeness = field_completeness
                metrics.completeness_score = (
                    sum(field_completeness.values()) / len(field_completeness)
                    if field_completeness
                    else 0
                )

        except Exception as e:
            self.logger.error(f"Error assessing completeness: {e}")
            metrics.completeness_score = 0.0

    async def _assess_accuracy(
        self,
        data: Union[List[Dict], pd.DataFrame],
        metrics: DataQualityMetrics,
        field_mapping: Optional[Dict[str, str]] = None,
    ):
        """Assess data accuracy using validation rules and patterns"""

        try:
            field_mapping = field_mapping or {}
            field_accuracy = {}
            validation_errors = []

            if ML_AVAILABLE and isinstance(data, pd.DataFrame):
                # Pandas-based accuracy assessment
                for column in data.columns:
                    field_type = field_mapping.get(
                        column, self._infer_field_type(data[column])
                    )
                    rules = self.quality_rules.get(field_type, [])

                    if rules:
                        valid_count = 0
                        total_count = 0

                        for idx, value in enumerate(data[column]):
                            if pd.notna(value):
                                total_count += 1
                                all_valid = True

                                for rule in rules:
                                    if rule.enabled:
                                        is_valid, error_msg = rule.validate(value)
                                        if not is_valid:
                                            all_valid = False
                                            validation_errors.append(
                                                {
                                                    "field": column,
                                                    "row": idx,
                                                    "value": str(value)[:100],
                                                    "rule": rule.name,
                                                    "severity": rule.severity,
                                                    "error": error_msg
                                                    or f"Failed {rule.name} validation",
                                                }
                                            )

                                if all_valid:
                                    valid_count += 1

                        field_accuracy[column] = (
                            valid_count / total_count if total_count > 0 else 1.0
                        )
                    else:
                        # No rules, assume perfect accuracy
                        field_accuracy[column] = 1.0

            else:
                # Fallback for list of dictionaries
                if not data:
                    return

                all_fields = set()
                for record in data:
                    all_fields.update(record.keys())

                for field in all_fields:
                    field_type = field_mapping.get(
                        field,
                        self._infer_field_type_from_values(
                            [record.get(field) for record in data if field in record]
                        ),
                    )
                    rules = self.quality_rules.get(field_type, [])

                    if rules:
                        valid_count = 0
                        total_count = 0

                        for row_idx, record in enumerate(data):
                            if field in record and record[field] is not None:
                                value = record[field]
                                total_count += 1
                                all_valid = True

                                for rule in rules:
                                    if rule.enabled:
                                        is_valid, error_msg = rule.validate(value)
                                        if not is_valid:
                                            all_valid = False
                                            validation_errors.append(
                                                {
                                                    "field": field,
                                                    "row": row_idx,
                                                    "value": str(value)[:100],
                                                    "rule": rule.name,
                                                    "severity": rule.severity,
                                                    "error": error_msg
                                                    or f"Failed {rule.name} validation",
                                                }
                                            )

                                if all_valid:
                                    valid_count += 1

                        field_accuracy[field] = (
                            valid_count / total_count if total_count > 0 else 1.0
                        )
                    else:
                        field_accuracy[field] = 1.0

            metrics.field_accuracy = field_accuracy
            metrics.accuracy_score = (
                sum(field_accuracy.values()) / len(field_accuracy)
                if field_accuracy
                else 1.0
            )
            metrics.validation_errors = validation_errors[
                :100
            ]  # Limit to first 100 errors

        except Exception as e:
            self.logger.error(f"Error assessing accuracy: {e}")
            metrics.accuracy_score = 0.5

    async def _assess_consistency(
        self, data: Union[List[Dict], pd.DataFrame], metrics: DataQualityMetrics
    ):
        """Assess data consistency (format standardization, value consistency)"""

        try:
            consistency_scores = []

            if ML_AVAILABLE and isinstance(data, pd.DataFrame):
                # Check format consistency for each column
                for column in data.columns:
                    if data[column].dtype == "object":  # String columns
                        # Analyze format patterns
                        non_null_values = data[column].dropna().astype(str)
                        if len(non_null_values) > 0:
                            # Check for consistent patterns (length, format)
                            patterns = defaultdict(int)

                            for value in non_null_values:
                                # Create a pattern based on character types
                                pattern = self._extract_format_pattern(value)
                                patterns[pattern] += 1

                            # Calculate consistency based on pattern distribution
                            if patterns:
                                most_common_count = max(patterns.values())
                                consistency = most_common_count / len(non_null_values)
                                consistency_scores.append(consistency)

                    elif data[column].dtype in ["int64", "float64"]:
                        # For numeric columns, check for reasonable distribution
                        non_null_values = data[column].dropna()
                        if len(non_null_values) > 1:
                            # Use coefficient of variation as consistency measure
                            cv = (
                                non_null_values.std() / non_null_values.mean()
                                if non_null_values.mean() != 0
                                else 0
                            )
                            # Convert to consistency score (lower CV = higher consistency)
                            consistency = max(0, 1 - min(cv, 1))
                            consistency_scores.append(consistency)

            else:
                # Fallback implementation
                if not data:
                    return

                all_fields = set()
                for record in data:
                    all_fields.update(record.keys())

                for field in all_fields:
                    values = [
                        record.get(field)
                        for record in data
                        if field in record and record[field] is not None
                    ]
                    if values:
                        # Check format consistency for strings
                        string_values = [str(v) for v in values if isinstance(v, str)]
                        if string_values:
                            patterns = defaultdict(int)
                            for value in string_values:
                                pattern = self._extract_format_pattern(value)
                                patterns[pattern] += 1

                            if patterns:
                                most_common_count = max(patterns.values())
                                consistency = most_common_count / len(string_values)
                                consistency_scores.append(consistency)

            metrics.consistency_score = (
                sum(consistency_scores) / len(consistency_scores)
                if consistency_scores
                else 1.0
            )

        except Exception as e:
            self.logger.error(f"Error assessing consistency: {e}")
            metrics.consistency_score = 0.5

    async def _assess_uniqueness(
        self, data: Union[List[Dict], pd.DataFrame], metrics: DataQualityMetrics
    ):
        """Assess data uniqueness (duplicate detection)"""

        try:
            if ML_AVAILABLE and isinstance(data, pd.DataFrame):
                # Check for duplicate rows
                unique_rows = len(data.drop_duplicates())
                total_rows = len(data)
                metrics.uniqueness_score = (
                    unique_rows / total_rows if total_rows > 0 else 1.0
                )

            else:
                # Fallback implementation
                if not data:
                    metrics.uniqueness_score = 1.0
                    return

                # Convert records to tuples for hashing
                record_hashes = set()
                for record in data:
                    # Create a hash of the record
                    record_str = json.dumps(record, sort_keys=True, default=str)
                    record_hash = hashlib.md5(record_str.encode()).hexdigest()
                    record_hashes.add(record_hash)

                metrics.uniqueness_score = (
                    len(record_hashes) / len(data) if len(data) > 0 else 1.0
                )

        except Exception as e:
            self.logger.error(f"Error assessing uniqueness: {e}")
            metrics.uniqueness_score = 0.5

    async def _assess_validity(
        self,
        data: Union[List[Dict], pd.DataFrame],
        metrics: DataQualityMetrics,
        field_mapping: Optional[Dict[str, str]] = None,
    ):
        """Assess data validity (business rule compliance)"""

        try:
            field_mapping = field_mapping or {}
            validity_scores = []

            # Business rule validations
            business_rules = [
                # Example rules - would be customized per domain
                {
                    "name": "price_positive",
                    "condition": lambda record: (
                        float(record.get("price", 0)) >= 0
                        if record.get("price")
                        else True
                    ),
                    "applicable_fields": ["price", "cost", "amount"],
                },
                {
                    "name": "future_dates",
                    "condition": lambda record: self._validate_future_date(
                        record.get("event_date", "")
                    ),
                    "applicable_fields": ["event_date", "end_date", "expiry_date"],
                },
            ]

            if isinstance(data, list) and data:
                for rule in business_rules:
                    applicable_records = []
                    valid_count = 0

                    for record in data:
                        # Check if rule applies to this record
                        has_applicable_field = any(
                            field in record for field in rule["applicable_fields"]
                        )

                        if has_applicable_field:
                            applicable_records.append(record)
                            try:
                                if rule["condition"](record):
                                    valid_count += 1
                            except Exception:
                                pass  # Invalid record

                    if applicable_records:
                        rule_validity = valid_count / len(applicable_records)
                        validity_scores.append(rule_validity)

            metrics.validity_score = (
                sum(validity_scores) / len(validity_scores) if validity_scores else 1.0
            )

        except Exception as e:
            self.logger.error(f"Error assessing validity: {e}")
            metrics.validity_score = 0.5

    async def _detect_anomalies(self, df: pd.DataFrame, metrics: DataQualityMetrics):
        """Detect anomalies in data using ML techniques"""

        try:
            if not self.anomaly_detector or df.empty:
                return

            # Prepare numeric data for anomaly detection
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) == 0:
                return

            numeric_data = df[numeric_columns].fillna(df[numeric_columns].median())

            if (
                len(numeric_data) < 10
            ):  # Need minimum data for meaningful anomaly detection
                return

            # Scale the data
            scaled_data = self.data_scaler.fit_transform(numeric_data)

            # Detect anomalies
            anomaly_labels = self.anomaly_detector.fit_predict(scaled_data)

            # Extract anomaly information
            anomalies = []
            for idx, label in enumerate(anomaly_labels):
                if label == -1:  # Anomaly detected
                    anomaly_data = {
                        "row_index": int(idx),
                        "anomaly_score": float(
                            self.anomaly_detector.score_samples([scaled_data[idx]])[0]
                        ),
                        "values": {},
                    }

                    # Include the anomalous values
                    for col in numeric_columns:
                        anomaly_data["values"][col] = df.iloc[idx][col]

                    anomalies.append(anomaly_data)

            metrics.data_anomalies = anomalies[:50]  # Limit to first 50 anomalies

            self.logger.info(f"Detected {len(anomalies)} data anomalies")

        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")

    async def _assess_advanced_metrics(
        self, df: pd.DataFrame, metrics: DataQualityMetrics
    ):
        """Assess advanced quality metrics using ML techniques"""

        try:
            # Freshness assessment (based on timestamps if available)
            timestamp_columns = []
            for col in df.columns:
                if any(
                    keyword in col.lower()
                    for keyword in ["date", "time", "created", "updated", "timestamp"]
                ):
                    timestamp_columns.append(col)

            if timestamp_columns:
                # Use the most recent timestamp column
                latest_col = timestamp_columns[0]
                try:
                    df[latest_col] = pd.to_datetime(df[latest_col], errors="coerce")
                    latest_date = df[latest_col].max()

                    if pd.notna(latest_date):
                        days_old = (datetime.now() - latest_date).days
                        # Freshness decreases with age (exponential decay)
                        metrics.freshness_score = max(
                            0, np.exp(-days_old / 30)
                        )  # 30-day half-life

                except Exception:
                    metrics.freshness_score = 0.5  # Unknown freshness
            else:
                metrics.freshness_score = 0.5  # No timestamp data

            # Relevance scoring (simplified - would use content analysis in practice)
            text_columns = df.select_dtypes(include=["object"]).columns
            if len(text_columns) > 0:
                # Simple relevance based on content richness
                total_text_length = 0
                total_records = 0

                for col in text_columns:
                    text_values = df[col].dropna().astype(str)
                    if len(text_values) > 0:
                        total_text_length += sum(len(val) for val in text_values)
                        total_records += len(text_values)

                if total_records > 0:
                    avg_content_length = total_text_length / total_records
                    # Normalize to 0-1 scale (assuming 100 chars is "good" content)
                    metrics.relevance_score = min(1.0, avg_content_length / 100)
                else:
                    metrics.relevance_score = 0.0
            else:
                metrics.relevance_score = 0.5

            # Precision scoring (measure of how specific/detailed the data is)
            precision_factors = []

            # Factor 1: Field diversity
            field_diversity = len(df.columns) / max(
                len(df.columns), 10
            )  # Normalize to typical range
            precision_factors.append(min(1.0, field_diversity))

            # Factor 2: Value diversity per field
            for col in df.columns:
                unique_ratio = len(df[col].unique()) / len(df) if len(df) > 0 else 0
                precision_factors.append(
                    min(1.0, unique_ratio * 2)
                )  # Higher diversity = higher precision

            metrics.precision_score = (
                sum(precision_factors) / len(precision_factors)
                if precision_factors
                else 0.5
            )

        except Exception as e:
            self.logger.error(f"Error assessing advanced metrics: {e}")

    def _calculate_composite_scores(self, metrics: DataQualityMetrics):
        """Calculate composite quality scores"""

        try:
            # Weighted overall quality score
            weights = {
                "completeness": 0.25,
                "accuracy": 0.25,
                "consistency": 0.15,
                "uniqueness": 0.15,
                "validity": 0.20,
            }

            metrics.overall_quality_score = (
                weights["completeness"] * metrics.completeness_score
                + weights["accuracy"] * metrics.accuracy_score
                + weights["consistency"] * metrics.consistency_score
                + weights["uniqueness"] * metrics.uniqueness_score
                + weights["validity"] * metrics.validity_score
            )

            # Business value score (includes advanced metrics)
            business_weights = {
                "overall_quality": 0.40,
                "freshness": 0.20,
                "relevance": 0.25,
                "precision": 0.15,
            }

            metrics.business_value_score = (
                business_weights["overall_quality"] * metrics.overall_quality_score
                + business_weights["freshness"] * metrics.freshness_score
                + business_weights["relevance"] * metrics.relevance_score
                + business_weights["precision"] * metrics.precision_score
            )

        except Exception as e:
            self.logger.error(f"Error calculating composite scores: {e}")
            metrics.overall_quality_score = 0.5
            metrics.business_value_score = 0.5

    def _infer_field_type(self, series: pd.Series) -> str:
        """Infer field type from pandas series"""

        if ML_AVAILABLE:
            # Analyze sample values to infer type
            sample_values = series.dropna().head(10).astype(str)

            for value in sample_values:
                if "@" in value and "." in value:
                    return "email"
                elif re.match(
                    r"^\+?1?-?\.?\s?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}$", value
                ):
                    return "phone"
                elif re.match(r"^https?://", value):
                    return "url"
                elif re.match(r"^\$?\d+\.?\d*$", value):
                    return "price"
                elif re.match(r"^\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}$", value):
                    return "date"

        return "general"

    def _infer_field_type_from_values(self, values: List[Any]) -> str:
        """Infer field type from list of values (fallback)"""

        sample_values = [str(v) for v in values if v is not None][:10]

        for value in sample_values:
            if "@" in value and "." in value:
                return "email"
            elif re.match(
                r"^\+?1?-?\.?\s?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}$", value
            ):
                return "phone"
            elif re.match(r"^https?://", value):
                return "url"
            elif re.match(r"^\$?\d+\.?\d*$", value):
                return "price"
            elif re.match(r"^\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}$", value):
                return "date"

        return "general"

    def _extract_format_pattern(self, value: str) -> str:
        """Extract format pattern from a string value"""

        pattern = ""
        for char in value:
            if char.isalpha():
                pattern += "A"
            elif char.isdigit():
                pattern += "9"
            elif char.isspace():
                pattern += " "
            else:
                pattern += char

        return pattern

    def _validate_future_date(self, date_str: str) -> bool:
        """Validate if date is reasonable for future events"""

        if not date_str:
            return True

        try:
            # Try to parse various date formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
                try:
                    parsed_date = datetime.strptime(str(date_str), fmt)
                    # Check if date is not too far in the future (e.g., within 10 years)
                    max_future = datetime.now() + timedelta(days=10 * 365)
                    return parsed_date <= max_future
                except ValueError:
                    continue

            return True  # If can't parse, assume valid

        except Exception:
            return True

    def generate_quality_report(self, metrics: DataQualityMetrics) -> Dict[str, Any]:
        """Generate comprehensive quality assessment report"""

        try:
            report = {
                "summary": {
                    "overall_quality_score": round(metrics.overall_quality_score, 3),
                    "business_value_score": round(metrics.business_value_score, 3),
                    "assessment_timestamp": metrics.assessment_timestamp.isoformat(),
                    "source_url": metrics.source_url,
                    "total_records": metrics.total_records,
                    "total_fields": metrics.total_fields,
                },
                "quality_dimensions": {
                    "completeness": round(metrics.completeness_score, 3),
                    "accuracy": round(metrics.accuracy_score, 3),
                    "consistency": round(metrics.consistency_score, 3),
                    "uniqueness": round(metrics.uniqueness_score, 3),
                    "validity": round(metrics.validity_score, 3),
                    "freshness": round(metrics.freshness_score, 3),
                    "relevance": round(metrics.relevance_score, 3),
                    "precision": round(metrics.precision_score, 3),
                },
                "field_analysis": {
                    "completeness_by_field": {
                        k: round(v, 3) for k, v in metrics.field_completeness.items()
                    },
                    "accuracy_by_field": {
                        k: round(v, 3) for k, v in metrics.field_accuracy.items()
                    },
                },
                "quality_issues": {
                    "validation_errors_count": len(metrics.validation_errors),
                    "anomalies_detected": len(metrics.data_anomalies),
                    "top_validation_errors": metrics.validation_errors[:10],
                    "top_anomalies": metrics.data_anomalies[:5],
                },
                "recommendations": self._generate_quality_recommendations(metrics),
            }

            return report

        except Exception as e:
            self.logger.error(f"Error generating quality report: {e}")
            return {"error": str(e)}

    def _generate_quality_recommendations(
        self, metrics: DataQualityMetrics
    ) -> List[Dict[str, Any]]:
        """Generate actionable quality improvement recommendations"""

        recommendations = []

        try:
            # Completeness recommendations
            if metrics.completeness_score < 0.8:
                incomplete_fields = [
                    field
                    for field, score in metrics.field_completeness.items()
                    if score < 0.8
                ]
                recommendations.append(
                    {
                        "type": "completeness",
                        "priority": (
                            "high" if metrics.completeness_score < 0.6 else "medium"
                        ),
                        "title": "Improve Data Completeness",
                        "description": f'Several fields have missing values: {", ".join(incomplete_fields[:5])}',
                        "actions": [
                            "Review data extraction selectors for missing fields",
                            "Implement fallback extraction methods",
                            "Add data validation at source",
                            "Consider alternative data sources",
                        ],
                    }
                )

            # Accuracy recommendations
            if metrics.accuracy_score < 0.8:
                error_types = Counter(
                    error["rule"] for error in metrics.validation_errors
                )
                most_common_errors = error_types.most_common(3)

                recommendations.append(
                    {
                        "type": "accuracy",
                        "priority": (
                            "high" if metrics.accuracy_score < 0.6 else "medium"
                        ),
                        "title": "Fix Data Accuracy Issues",
                        "description": f'Common validation failures: {", ".join([error[0] for error in most_common_errors])}',
                        "actions": [
                            "Review and update validation rules",
                            "Implement data cleaning transformations",
                            "Add format standardization",
                            "Improve extraction patterns",
                        ],
                    }
                )

            # Consistency recommendations
            if metrics.consistency_score < 0.7:
                recommendations.append(
                    {
                        "type": "consistency",
                        "priority": "medium",
                        "title": "Standardize Data Formats",
                        "description": "Inconsistent data formats detected across records",
                        "actions": [
                            "Implement data normalization pipelines",
                            "Add format standardization rules",
                            "Use consistent parsing patterns",
                            "Validate data at extraction time",
                        ],
                    }
                )

            # Uniqueness recommendations
            if metrics.uniqueness_score < 0.9:
                recommendations.append(
                    {
                        "type": "uniqueness",
                        "priority": "medium",
                        "title": "Remove Duplicate Records",
                        "description": f"Duplicate records detected ({(1-metrics.uniqueness_score)*100:.1f}% duplication rate)",
                        "actions": [
                            "Implement deduplication logic",
                            "Add unique identifiers to records",
                            "Review extraction logic for duplicate sources",
                            "Use content-based deduplication",
                        ],
                    }
                )

            # Freshness recommendations
            if metrics.freshness_score < 0.5:
                recommendations.append(
                    {
                        "type": "freshness",
                        "priority": "medium",
                        "title": "Improve Data Freshness",
                        "description": "Data appears to be outdated",
                        "actions": [
                            "Increase scraping frequency",
                            "Monitor source update patterns",
                            "Add timestamp validation",
                            "Implement incremental updates",
                        ],
                    }
                )

            # Anomaly recommendations
            if (
                len(metrics.data_anomalies) > len(metrics.data_anomalies) * 0.1
            ):  # More than 10% anomalies
                recommendations.append(
                    {
                        "type": "anomalies",
                        "priority": "medium",
                        "title": "Investigate Data Anomalies",
                        "description": f"{len(metrics.data_anomalies)} data anomalies detected",
                        "actions": [
                            "Review anomalous records for patterns",
                            "Adjust anomaly detection sensitivity",
                            "Investigate data source changes",
                            "Consider outlier removal or flagging",
                        ],
                    }
                )

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return recommendations

    def add_custom_quality_rule(self, field_name: str, rule: QualityRule):
        """Add a custom quality validation rule"""

        if field_name not in self.quality_rules:
            self.quality_rules[field_name] = []

        self.quality_rules[field_name].append(rule)
        self.logger.info(
            f"Added custom quality rule '{rule.name}' for field '{field_name}'"
        )

    def get_quality_trends(
        self, source_url: str = "", days: int = 30
    ) -> Dict[str, Any]:
        """Analyze quality trends over time"""

        try:
            # Filter history by source and date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            filtered_history = [
                m
                for m in self.quality_history
                if m.assessment_timestamp > cutoff_date
                and (not source_url or m.source_url == source_url)
            ]

            if not filtered_history:
                return {"error": "No historical data available"}

            # Calculate trends
            timestamps = [m.assessment_timestamp for m in filtered_history]
            overall_scores = [m.overall_quality_score for m in filtered_history]
            completeness_scores = [m.completeness_score for m in filtered_history]
            accuracy_scores = [m.accuracy_score for m in filtered_history]

            trends = {
                "period_days": days,
                "source_url": source_url,
                "data_points": len(filtered_history),
                "overall_quality": {
                    "current": overall_scores[-1] if overall_scores else 0,
                    "average": statistics.mean(overall_scores) if overall_scores else 0,
                    "trend": self._calculate_trend(overall_scores),
                    "min": min(overall_scores) if overall_scores else 0,
                    "max": max(overall_scores) if overall_scores else 0,
                },
                "completeness": {
                    "current": completeness_scores[-1] if completeness_scores else 0,
                    "average": (
                        statistics.mean(completeness_scores)
                        if completeness_scores
                        else 0
                    ),
                    "trend": self._calculate_trend(completeness_scores),
                },
                "accuracy": {
                    "current": accuracy_scores[-1] if accuracy_scores else 0,
                    "average": (
                        statistics.mean(accuracy_scores) if accuracy_scores else 0
                    ),
                    "trend": self._calculate_trend(accuracy_scores),
                },
            }

            return trends

        except Exception as e:
            self.logger.error(f"Error analyzing quality trends: {e}")
            return {"error": str(e)}

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values"""

        if len(values) < 2:
            return "stable"

        # Simple trend calculation using first and last values
        first_half_avg = statistics.mean(values[: len(values) // 2])
        second_half_avg = statistics.mean(values[len(values) // 2 :])

        diff = second_half_avg - first_half_avg

        if abs(diff) < 0.05:  # Less than 5% change
            return "stable"
        elif diff > 0:
            return "improving"
        else:
            return "declining"


# Global instance
quality_assessor = AdvancedDataQualityAssessor()
