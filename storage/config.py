"""
CFPL Configuration System
Centralized configuration for Capture-First, Process-Later architecture
"""

import json
import os
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class CaptureConfig:
    """Configuration for content capture"""
    mode: str = "cas"  # "cas" or "warc"
    render_dom: bool = True
    har: bool = True
    media: str = "network_first"  # "network_first", "screencast_fallback", "off"
    assets: bool = True
    follow_redirects: bool = True
    max_redirects: int = 10


@dataclass 
class StorageConfig:
    """Configuration for storage backend"""
    root: str = "./storage"
    backend: str = "filesystem"  # "filesystem", "s3"
    s3_bucket: Optional[str] = None
    s3_prefix: Optional[str] = None
    compression: bool = False
    encryption: bool = False


@dataclass
class LimitsConfig:
    """Configuration for resource limits"""
    max_asset_bytes: int = 100 * 1024 * 1024  # 100MB
    max_content_bytes: int = 50 * 1024 * 1024   # 50MB
    concurrent_fetches: int = 10
    concurrent_per_domain: int = 2
    timeout_sec: int = 30
    rate_limit_rps: float = 2.0


@dataclass
class PrivacyConfig:
    """Configuration for privacy and security"""
    redact_headers: List[str] = field(default_factory=lambda: [
        "Authorization", "Cookie", "X-API-Key", "X-Auth-Token"
    ])
    redact_query_params: List[str] = field(default_factory=lambda: [
        "api_key", "token", "auth", "password"
    ])
    log_full_urls: bool = False
    encrypt_sensitive_data: bool = False


@dataclass 
class RetentionConfig:
    """Configuration for data retention"""
    raw_years: int = 2
    derived_days: int = 90
    cleanup_interval_hours: int = 24
    auto_cleanup: bool = True


@dataclass
class ProcessingConfig:
    """Configuration for post-capture processing"""
    enabled_processors: List[str] = field(default_factory=lambda: [
        "html_parser", "text_extractor", "media_metadata"
    ])
    async_processing: bool = True
    max_processing_workers: int = 4
    retry_failed: bool = True
    retry_max_attempts: int = 3


@dataclass
class CFPLConfig:
    """Complete CFPL configuration"""
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    limits: LimitsConfig = field(default_factory=LimitsConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    retention: RetentionConfig = field(default_factory=RetentionConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    
    # Operational settings
    run_id_prefix: str = "cfpl"
    log_level: str = "INFO"
    metrics_enabled: bool = True
    health_check_interval: int = 300  # seconds


class CFPLConfigManager:
    """Manager for CFPL configuration loading and validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._default_config_path()
        self._config: Optional[CFPLConfig] = None
    
    def _default_config_path(self) -> str:
        """Get default configuration file path"""
        # Check environment variable first
        if "CFPL_CONFIG" in os.environ:
            return os.environ["CFPL_CONFIG"]
            
        # Check various standard locations
        candidates = [
            "./cfpl_config.json",
            "./config/cfpl_config.json", 
            str(Path.home() / ".cfpl" / "config.json"),
            "/etc/cfpl/config.json"
        ]
        
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
                
        # Default to current directory
        return "./cfpl_config.json"
    
    def load_config(self) -> CFPLConfig:
        """Load configuration from file or create default"""
        if not os.path.exists(self.config_path):
            logger.info(f"Config file not found at {self.config_path}, creating default")
            self._config = CFPLConfig()
            self.save_config()
        else:
            logger.info(f"Loading configuration from {self.config_path}")
            with open(self.config_path, 'r') as f:
                config_dict = json.load(f)
            self._config = self._dict_to_config(config_dict)
            
        self._validate_config()
        return self._config
    
    def save_config(self):
        """Save current configuration to file"""
        if not self._config:
            raise ValueError("No configuration loaded to save")
            
        # Ensure directory exists
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and save
        config_dict = asdict(self._config)
        
        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Configuration saved to {self.config_path}")
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> CFPLConfig:
        """Convert dictionary to CFPLConfig object"""
        try:
            return CFPLConfig(
                capture=CaptureConfig(**config_dict.get('capture', {})),
                storage=StorageConfig(**config_dict.get('storage', {})),
                limits=LimitsConfig(**config_dict.get('limits', {})),
                privacy=PrivacyConfig(**config_dict.get('privacy', {})),
                retention=RetentionConfig(**config_dict.get('retention', {})),
                processing=ProcessingConfig(**config_dict.get('processing', {})),
                run_id_prefix=config_dict.get('run_id_prefix', 'cfpl'),
                log_level=config_dict.get('log_level', 'INFO'),
                metrics_enabled=config_dict.get('metrics_enabled', True),
                health_check_interval=config_dict.get('health_check_interval', 300)
            )
        except Exception as e:
            logger.error(f"Failed to parse configuration: {e}")
            logger.info("Falling back to default configuration")
            return CFPLConfig()
    
    def _validate_config(self):
        """Validate configuration values"""
        if not self._config:
            raise ValueError("No configuration to validate")
            
        config = self._config
        
        # Validate capture mode
        if config.capture.mode not in ["cas", "warc"]:
            raise ValueError(f"Invalid capture mode: {config.capture.mode}")
            
        # Validate media capture mode  
        valid_media_modes = ["network_first", "screencast_fallback", "off"]
        if config.capture.media not in valid_media_modes:
            raise ValueError(f"Invalid media capture mode: {config.capture.media}")
            
        # Validate storage backend
        if config.storage.backend not in ["filesystem", "s3"]:
            raise ValueError(f"Invalid storage backend: {config.storage.backend}")
            
        # Validate S3 configuration if needed
        if config.storage.backend == "s3" and not config.storage.s3_bucket:
            raise ValueError("S3 bucket required when using S3 storage backend")
            
        # Validate limits
        if config.limits.concurrent_fetches <= 0:
            raise ValueError("concurrent_fetches must be positive")
            
        if config.limits.concurrent_per_domain <= 0:
            raise ValueError("concurrent_per_domain must be positive")
            
        if config.limits.timeout_sec <= 0:
            raise ValueError("timeout_sec must be positive")
            
        # Validate retention
        if config.retention.raw_years <= 0:
            logger.warning("raw_years should be positive for data retention")
            
        if config.retention.derived_days <= 0:
            logger.warning("derived_days should be positive for data retention")
            
        # Validate processing
        valid_processors = [
            "html_parser", "text_extractor", "media_metadata", 
            "image_thumbs", "ocr", "transcripts", "embeddings"
        ]
        
        for processor in config.processing.enabled_processors:
            if processor not in valid_processors:
                logger.warning(f"Unknown processor: {processor}")
                
        # Create storage root if it doesn't exist
        if config.storage.backend == "filesystem":
            storage_path = Path(config.storage.root)
            storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Storage root verified: {storage_path}")
    
    def get_config(self) -> CFPLConfig:
        """Get current configuration, loading if necessary"""
        if not self._config:
            return self.load_config()
        return self._config
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        if not self._config:
            self.load_config()
            
        # Apply updates to nested structures
        config_dict = asdict(self._config)
        self._deep_update(config_dict, updates)
        
        # Reload from updated dict
        self._config = self._dict_to_config(config_dict)
        self._validate_config()
        
        # Save updated configuration
        self.save_config()
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]):
        """Deep update dictionary with nested structure support"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


# Global configuration instance
config_manager = CFPLConfigManager()


def get_config() -> CFPLConfig:
    """Get global CFPL configuration"""
    return config_manager.get_config()


def load_config_from_file(config_path: str) -> CFPLConfig:
    """Load configuration from specific file path"""
    manager = CFPLConfigManager(config_path)
    return manager.load_config()


def create_default_config(config_path: str) -> CFPLConfig:
    """Create and save default configuration to specified path"""
    manager = CFPLConfigManager(config_path)
    config = CFPLConfig()
    manager._config = config
    manager.save_config()
    return config
