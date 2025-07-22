#!/usr/bin/env python3
"""
Integration Test Script for Advanced Features

This script tests all 8 advanced features to ensure they load correctly
and basic functionality works as expected.
"""

import sys
import logging
import traceback
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_dependencies():
    """Test if all required dependencies are installed"""
    logger.info("Testing dependencies...")
    
    required_packages = [
        'PyQt6', 'plotly', 'networkx', 'numpy', 'aiohttp', 'bs4',
        'transformers', 'torch', 'cv2', 'pytesseract', 'stem', 'socks',
        'selenium', 'PIL', 'nltk', 'textblob', 'pandas', 'sqlalchemy',
        'spacy', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
            logger.info(f"✓ {package} - OK")
        except ImportError as e:
            logger.error(f"✗ {package} - MISSING: {e}")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {missing_packages}")
        return False
    
    logger.info("All dependencies installed successfully!")
    return True

def test_ml_models():
    """Test ML models are available"""
    logger.info("Testing ML models...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("This is a test sentence.")
        logger.info(f"✓ spaCy model loaded, processed {len(doc)} tokens")
    except Exception as e:
        logger.error(f"✗ spaCy model failed: {e}")
        return False
    
    try:
        import nltk
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        score = analyzer.polarity_scores("This is a positive test.")
        logger.info(f"✓ NLTK VADER loaded, test score: {score['compound']:.2f}")
    except Exception as e:
        logger.error(f"✗ NLTK models failed: {e}")
        return False
    
    logger.info("ML models loaded successfully!")
    return True

def test_gui_components():
    """Test GUI components can be imported"""
    logger.info("Testing GUI components...")
    
    # We need to create a QApplication for Qt widgets
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Set WebEngine attributes before creating QApplication
        if not QApplication.instance():
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
            app = QApplication([])
        else:
            app = QApplication.instance()
    except Exception as e:
        logger.error(f"✗ Could not create QApplication: {e}")
        return False
    
    components = [
        ("tooltip_system", "TooltipManager"),
        ("tor_integration", "TORWidget"),
        ("network_config", "NetworkConfigWidget"),
        ("advanced_parsing", "ParsingWidget"),
        ("embedded_browser", "EmbeddedBrowserWidget"),
        ("data_visualization", "SiteVisualizationWidget"),
        ("osint_integration", "OSINTIntegrationWidget"),
        ("data_enrichment", "DataEnrichmentWidget")
    ]
    
    failed_components = []
    
    for module_name, class_name in components:
        try:
            # Add gui components to path
            gui_path = Path(__file__).parent / "gui" / "components"
            if str(gui_path) not in sys.path:
                sys.path.insert(0, str(gui_path))
            
            module = __import__(module_name)
            widget_class = getattr(module, class_name)
            
            # For simple test, just verify class exists
            logger.info(f"✓ {module_name}.{class_name} - OK")
            
        except Exception as e:
            logger.error(f"✗ {module_name}.{class_name} - FAILED: {e}")
            failed_components.append(f"{module_name}.{class_name}")
    
    if failed_components:
        logger.error(f"Failed components: {failed_components}")
        return False
    
    logger.info("All GUI components imported successfully!")
    return True

def test_configuration():
    """Test configuration system"""
    logger.info("Testing configuration system...")
    
    try:
        # Add config to path
        config_path = Path(__file__).parent / "config"
        if str(config_path) not in sys.path:
            sys.path.insert(0, str(config_path))
        
        from config_loader import get_config, save_config
        
        config = get_config()
        logger.info(f"✓ Configuration loaded: {len(config)} sections")
        
        # Test that basic sections exist
        expected_sections = [
            "api_credentials", "vpn_providers", "proxy_pools", 
            "tor_config", "spiderfoot_config"
        ]
        
        missing_sections = []
        for section in expected_sections:
            if section not in config:
                missing_sections.append(section)
                
        if missing_sections:
            logger.warning(f"Missing config sections: {missing_sections}")
        else:
            logger.info("✓ All configuration sections present")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Configuration system failed: {e}")
        return False

def test_dashboard_integration():
    """Test main dashboard integration"""
    logger.info("Testing dashboard integration...")
    
    try:
        # Add gui components to path
        gui_path = Path(__file__).parent / "gui" / "components"
        if str(gui_path) not in sys.path:
            sys.path.insert(0, str(gui_path))
        
        from dashboard import DashboardWindow
        
        # Create QApplication if needed
        from PyQt6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        
        # Test dashboard creation (don't show it)
        dashboard = DashboardWindow()
        
        # Check that all expected components are present
        expected_components = [
            'job_manager', 'log_viewer', 'data_viewer', 'tor_widget',
            'network_config', 'parsing_widget', 'browser_tabs',
            'visualization_widget', 'osint_widget', 'enrichment_widget'
        ]
        
        missing_components = []
        for component in expected_components:
            if not hasattr(dashboard, component):
                missing_components.append(component)
        
        if missing_components:
            logger.error(f"Missing dashboard components: {missing_components}")
            return False
        
        logger.info("✓ Dashboard integration successful!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Dashboard integration failed: {e}")
        logger.error(f"Error details: {traceback.format_exc()}")
        return False

def test_basic_functionality():
    """Test basic functionality of key components"""
    logger.info("Testing basic functionality...")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: TOR configuration
    total_tests += 1
    try:
        config_path = Path(__file__).parent / "config"
        if str(config_path) not in sys.path:
            sys.path.insert(0, str(config_path))
        
        from config_loader import get_config
        config = get_config()
        tor_config = config.get("tor_config", {})
        
        if tor_config.get("enabled", False):
            logger.info("✓ TOR configuration enabled")
            tests_passed += 1
        else:
            logger.warning("⚠ TOR configuration disabled (this is OK)")
            tests_passed += 1
    except Exception as e:
        logger.error(f"✗ TOR configuration test failed: {e}")
    
    # Test 2: Data visualization
    total_tests += 1
    try:
        gui_path = Path(__file__).parent / "gui" / "components"
        if str(gui_path) not in sys.path:
            sys.path.insert(0, str(gui_path))
        
        from data_visualization import NetworkLayoutEngine
        
        engine = NetworkLayoutEngine(mode="2d")
        logger.info("✓ Visualization engine created")
        tests_passed += 1
    except Exception as e:
        logger.error(f"✗ Visualization test failed: {e}")
    
    # Test 3: OSINT modules
    total_tests += 1
    try:
        from osint_integration import OSINTModule
        
        class TestModule(OSINTModule):
            def __init__(self):
                super().__init__("test")
            
            def can_handle(self, target_type):
                return True
            
            async def investigate(self, target):
                return []
        
        module = TestModule()
        logger.info("✓ OSINT module system working")
        tests_passed += 1
    except Exception as e:
        logger.error(f"✗ OSINT test failed: {e}")
    
    logger.info(f"Basic functionality tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests

def main():
    """Run all tests"""
    logger.info("Starting integration test suite...")
    logger.info("=" * 50)
    
    all_tests_passed = True
    
    # Test 1: Dependencies
    if not test_dependencies():
        all_tests_passed = False
    
    print()
    
    # Test 2: ML Models
    if not test_ml_models():
        all_tests_passed = False
    
    print()
    
    # Test 3: Configuration
    if not test_configuration():
        all_tests_passed = False
    
    print()
    
    # Test 4: GUI Components
    if not test_gui_components():
        all_tests_passed = False
    
    print()
    
    # Test 5: Dashboard Integration
    if not test_dashboard_integration():
        all_tests_passed = False
    
    print()
    
    # Test 6: Basic Functionality
    if not test_basic_functionality():
        all_tests_passed = False
    
    print()
    logger.info("=" * 50)
    
    if all_tests_passed:
        logger.info("🎉 ALL TESTS PASSED! Integration successful!")
        logger.info("\nNext steps:")
        logger.info("1. Configure API credentials in config/api_config.py")
        logger.info("2. Run the dashboard: python -m gui.main")
        logger.info("3. Test individual features in the GUI")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        logger.info("\nTroubleshooting:")
        logger.info("1. Install dependencies: pip install -r requirements.txt")
        logger.info("2. Download missing models: python -m spacy download en_core_web_sm")
        logger.info("3. Check error messages for specific issues")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
