"""
AI Configuration Management
Handles AI model configuration, loading, and environment setup
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ModelType(Enum):
    SPACY = "spacy"
    TRANSFORMERS = "transformers"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OPENAI = "openai"


@dataclass
class ModelConfig:
    """Configuration for individual AI models"""

    name: str
    type: ModelType
    enabled: bool = True
    model_path: Optional[str] = None
    api_key: Optional[str] = None
    cache_size: int = 1000
    batch_size: int = 32
    timeout: int = 30
    custom_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}


@dataclass
class AIConfig:
    """Main AI configuration"""

    enabled: bool = True
    models: Dict[str, ModelConfig] = None
    cache_dir: str = "./data/ai_cache"
    log_level: str = "INFO"
    max_text_length: int = 10000
    parallel_processing: bool = True
    max_workers: int = 4

    def __post_init__(self):
        if self.models is None:
            self.models = self._get_default_models()

    def _get_default_models(self) -> Dict[str, ModelConfig]:
        """Get default model configurations"""
        return {
            "spacy_en": ModelConfig(
                name="en_core_web_sm",
                type=ModelType.SPACY,
                enabled=True,
                custom_params={
                    "disable": ["parser", "tagger"],  # Keep only NER
                    "max_length": 1000000,
                },
            ),
            "sentiment_classifier": ModelConfig(
                name="cardiffnlp/twitter-roberta-base-sentiment-latest",
                type=ModelType.TRANSFORMERS,
                enabled=True,
                batch_size=16,
                custom_params={
                    "return_all_scores": True,
                    "truncation": True,
                    "max_length": 512,
                },
            ),
            "text_classifier": ModelConfig(
                name="facebook/bart-large-mnli",
                type=ModelType.TRANSFORMERS,
                enabled=True,
                custom_params={
                    "candidate_labels": [
                        "business",
                        "technology",
                        "finance",
                        "news",
                        "job posting",
                        "product",
                        "service",
                        "research",
                    ]
                },
            ),
            "summarizer": ModelConfig(
                name="facebook/bart-large-cnn",
                type=ModelType.TRANSFORMERS,
                enabled=True,
                custom_params={"max_length": 150, "min_length": 30, "do_sample": False},
            ),
            "sentence_embeddings": ModelConfig(
                name="all-MiniLM-L6-v2",
                type=ModelType.SENTENCE_TRANSFORMERS,
                enabled=True,
                custom_params={"normalize_embeddings": True},
            ),
            "openai_gpt": ModelConfig(
                name="gpt-3.5-turbo",
                type=ModelType.OPENAI,
                enabled=False,  # Disabled by default
                api_key=None,  # Set via environment variable
                custom_params={"temperature": 0.3, "max_tokens": 150},
            ),
        }


class AIConfigManager:
    """Manages AI configuration loading, saving, and validation"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        return str(Path(__file__).parent.parent.parent / "config" / "ai_config.yaml")

    def _load_config(self) -> AIConfig:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = yaml.safe_load(f)
                return self._dict_to_config(data)
            except Exception as e:
                print(f"Error loading AI config: {e}. Using defaults.")

        # Create default config and save it
        config = AIConfig()
        self.save_config(config)
        return config

    def _dict_to_config(self, data: Dict[str, Any]) -> AIConfig:
        """Convert dictionary to AIConfig object"""
        models = {}
        if "models" in data:
            for name, model_data in data["models"].items():
                model_type = ModelType(model_data.get("type", "transformers"))
                models[name] = ModelConfig(
                    name=model_data.get("name", name),
                    type=model_type,
                    enabled=model_data.get("enabled", True),
                    model_path=model_data.get("model_path"),
                    api_key=model_data.get("api_key"),
                    cache_size=model_data.get("cache_size", 1000),
                    batch_size=model_data.get("batch_size", 32),
                    timeout=model_data.get("timeout", 30),
                    custom_params=model_data.get("custom_params", {}),
                )

        return AIConfig(
            enabled=data.get("enabled", True),
            models=models,
            cache_dir=data.get("cache_dir", "./data/ai_cache"),
            log_level=data.get("log_level", "INFO"),
            max_text_length=data.get("max_text_length", 10000),
            parallel_processing=data.get("parallel_processing", True),
            max_workers=data.get("max_workers", 4),
        )

    def _config_to_dict(self, config: AIConfig) -> Dict[str, Any]:
        """Convert AIConfig object to dictionary"""
        models_dict = {}
        for name, model in config.models.items():
            models_dict[name] = {
                "name": model.name,
                "type": model.type.value,
                "enabled": model.enabled,
                "model_path": model.model_path,
                "api_key": model.api_key,
                "cache_size": model.cache_size,
                "batch_size": model.batch_size,
                "timeout": model.timeout,
                "custom_params": model.custom_params,
            }

        return {
            "enabled": config.enabled,
            "models": models_dict,
            "cache_dir": config.cache_dir,
            "log_level": config.log_level,
            "max_text_length": config.max_text_length,
            "parallel_processing": config.parallel_processing,
            "max_workers": config.max_workers,
        }

    def save_config(self, config: AIConfig = None):
        """Save configuration to file"""
        if config is None:
            config = self.config

        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        config_dict = self._config_to_dict(config)

        with open(self.config_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)

    def get_config(self) -> AIConfig:
        """Get current configuration"""
        return self.config

    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        config_dict = self._config_to_dict(self.config)
        config_dict.update(updates)
        self.config = self._dict_to_config(config_dict)
        self.save_config()

    def enable_model(self, model_name: str):
        """Enable a specific model"""
        if model_name in self.config.models:
            self.config.models[model_name].enabled = True
            self.save_config()

    def disable_model(self, model_name: str):
        """Disable a specific model"""
        if model_name in self.config.models:
            self.config.models[model_name].enabled = False
            self.save_config()

    def set_openai_key(self, api_key: str):
        """Set OpenAI API key"""
        if "openai_gpt" in self.config.models:
            self.config.models["openai_gpt"].api_key = api_key
            self.config.models["openai_gpt"].enabled = True
            self.save_config()

    def add_custom_model(self, name: str, model_config: ModelConfig):
        """Add a custom model configuration"""
        self.config.models[name] = model_config
        self.save_config()

    def remove_model(self, model_name: str):
        """Remove a model configuration"""
        if model_name in self.config.models:
            del self.config.models[model_name]
            self.save_config()

    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []

        # Check if cache directory is writable
        try:
            os.makedirs(self.config.cache_dir, exist_ok=True)
            test_file = os.path.join(self.config.cache_dir, ".test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            issues.append(f"Cache directory not writable: {e}")

        # Check model configurations
        for name, model in self.config.models.items():
            if model.enabled:
                if model.type == ModelType.OPENAI and not model.api_key:
                    # Check for API key in environment
                    if not os.getenv("OPENAI_API_KEY"):
                        issues.append(
                            f"OpenAI model {name} enabled but no API key provided"
                        )

                if model.batch_size <= 0:
                    issues.append(
                        f"Model {name} has invalid batch_size: {model.batch_size}"
                    )

                if model.timeout <= 0:
                    issues.append(f"Model {name} has invalid timeout: {model.timeout}")

        return issues

    def get_environment_variables(self) -> Dict[str, str]:
        """Get recommended environment variables for AI setup"""
        env_vars = {}

        # Check for models requiring environment setup
        for name, model in self.config.models.items():
            if model.enabled:
                if model.type == ModelType.OPENAI:
                    env_vars["OPENAI_API_KEY"] = model.api_key or "your-openai-api-key"
                elif model.type == ModelType.TRANSFORMERS:
                    env_vars["TRANSFORMERS_CACHE"] = os.path.join(
                        self.config.cache_dir, "transformers"
                    )
                elif model.type == ModelType.SENTENCE_TRANSFORMERS:
                    env_vars["SENTENCE_TRANSFORMERS_HOME"] = os.path.join(
                        self.config.cache_dir, "sentence_transformers"
                    )

        # Common AI environment variables
        env_vars.update(
            {
                "TOKENIZERS_PARALLELISM": "false",  # Avoid warnings
                "AI_CACHE_DIR": self.config.cache_dir,
                "AI_LOG_LEVEL": self.config.log_level,
            }
        )

        return env_vars

    def generate_requirements(self) -> List[str]:
        """Generate Python requirements based on enabled models"""
        requirements = []

        enabled_types = set()
        for model in self.config.models.values():
            if model.enabled:
                enabled_types.add(model.type)

        # Add requirements based on enabled model types
        if ModelType.SPACY in enabled_types:
            requirements.extend(
                [
                    "spacy>=3.4.0",
                    "en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.4.0/en_core_web_sm-3.4.0.tar.gz",
                ]
            )

        if ModelType.TRANSFORMERS in enabled_types:
            requirements.extend(
                ["transformers>=4.20.0", "torch>=1.12.0", "tokenizers>=0.12.0"]
            )

        if ModelType.SENTENCE_TRANSFORMERS in enabled_types:
            requirements.append("sentence-transformers>=2.2.0")

        if ModelType.OPENAI in enabled_types:
            requirements.append("openai>=1.0.0")

        # Common dependencies
        requirements.extend(["numpy>=1.21.0", "scikit-learn>=1.1.0"])

        return sorted(set(requirements))


# Global config manager instance
_config_manager = None


def get_config_manager() -> AIConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = AIConfigManager()
    return _config_manager


def get_ai_config() -> AIConfig:
    """Get current AI configuration"""
    return get_config_manager().get_config()


# CLI helper functions for configuration management
def setup_ai_config():
    """Interactive setup for AI configuration"""
    print("AI Configuration Setup")
    print("=====================")

    config_manager = get_config_manager()
    config = config_manager.get_config()

    # Enable/disable AI entirely
    ai_enabled = input("Enable AI features? [Y/n]: ").lower() not in ["n", "no"]
    config.enabled = ai_enabled

    if not ai_enabled:
        config_manager.save_config(config)
        print("AI features disabled.")
        return

    # Configure models
    print("\nModel Configuration:")
    for name, model in config.models.items():
        current_status = "enabled" if model.enabled else "disabled"
        enable = input(
            f"Enable {name} ({model.type.value})? [{current_status}] [Y/n]: "
        )
        model.enabled = enable.lower() not in ["n", "no"]

        if model.enabled and model.type == ModelType.OPENAI:
            api_key = input(
                f"OpenAI API key (current: {'set' if model.api_key else 'not set'}): "
            )
            if api_key:
                model.api_key = api_key

    # Cache configuration
    cache_dir = input(f"Cache directory [{config.cache_dir}]: ") or config.cache_dir
    config.cache_dir = cache_dir

    # Save configuration
    config_manager.save_config(config)

    # Validate and show issues
    issues = config_manager.validate_config()
    if issues:
        print("\nConfiguration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nConfiguration saved successfully!")

    # Show environment variables
    env_vars = config_manager.get_environment_variables()
    if env_vars:
        print("\nRecommended Environment Variables:")
        for key, value in env_vars.items():
            print(f"  export {key}={value}")

    # Show requirements
    requirements = config_manager.generate_requirements()
    print(f"\nPython Requirements ({len(requirements)} packages):")
    for req in requirements:
        print(f"  {req}")


if __name__ == "__main__":
    setup_ai_config()
