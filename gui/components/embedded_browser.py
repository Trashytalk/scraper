"""
Embedded Chromium Browser with Recording and Playback Capabilities
"""
from PyQt6.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEnginePage
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLineEdit, QTabWidget, QDockWidget, QMainWindow,
                            QProgressBar, QLabel, QComboBox, QSpinBox, QCheckBox,
                            QTextEdit, QSplitter, QToolBar)
from PyQt6.QtCore import QUrl, pyqtSignal, QThread, QTimer, QSettings
from PyQt6.QtGui import QAction, QIcon
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class BrowserAction:
    """Represents a recorded browser action"""
    timestamp: float
    action_type: str  # 'navigate', 'click', 'type', 'scroll', 'wait'
    selector: Optional[str] = None
    value: Optional[str] = None
    coordinates: Optional[tuple] = None
    url: Optional[str] = None

class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepts and logs web requests for recording"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recorded_requests = []
        self.recording = False
        
    def interceptRequest(self, info):
        """Intercept and potentially modify requests"""
        if self.recording:
            request_data = {
                'url': info.requestUrl().toString(),
                'method': info.requestMethod().data().decode(),
                'timestamp': time.time()
            }
            self.recorded_requests.append(request_data)
            
        # Allow request to proceed
        pass

class BrowserRecorder:
    """Records browser interactions for playback"""
    
    def __init__(self):
        self.actions: List[BrowserAction] = []
        self.recording = False
        self.start_time = None
        
    def start_recording(self):
        """Start recording browser actions"""
        self.actions.clear()
        self.recording = True
        self.start_time = time.time()
        logger.info("Browser recording started")
        
    def stop_recording(self):
        """Stop recording browser actions"""
        self.recording = False
        logger.info(f"Browser recording stopped. Recorded {len(self.actions)} actions")
        
    def record_action(self, action_type: str, **kwargs):
        """Record a browser action"""
        if not self.recording:
            return
            
        action = BrowserAction(
            timestamp=time.time() - self.start_time,
            action_type=action_type,
            **kwargs
        )
        self.actions.append(action)
        
    def save_recording(self, filepath: str):
        """Save recorded actions to file"""
        with open(filepath, 'w') as f:
            json.dump([asdict(action) for action in self.actions], f, indent=2)
            
    def load_recording(self, filepath: str):
        """Load recorded actions from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.actions = [BrowserAction(**action_data) for action_data in data]

class BrowserPlayer(QThread):
    """Plays back recorded browser actions"""
    
    action_executed = pyqtSignal(str, dict)
    playback_finished = pyqtSignal()
    
    def __init__(self, browser_view, actions: List[BrowserAction]):
        super().__init__()
        self.browser_view = browser_view
        self.actions = actions
        self.playing = False
        
    def run(self):
        """Execute playback in separate thread"""
        self.playing = True
        
        for action in self.actions:
            if not self.playing:
                break
                
            # Wait for action timestamp
            if len(self.actions) > 1:
                self.msleep(int(action.timestamp * 1000))
                
            self.execute_action(action)
            
        self.playback_finished.emit()
        
    def execute_action(self, action: BrowserAction):
        """Execute a recorded action"""
        action_data = asdict(action)
        
        if action.action_type == 'navigate':
            self.browser_view.load(QUrl(action.url))
        elif action.action_type == 'click':
            # Execute click via JavaScript
            js_code = f"document.querySelector('{action.selector}').click();"
            self.browser_view.page().runJavaScript(js_code)
        elif action.action_type == 'type':
            # Execute typing via JavaScript
            js_code = f"""
            var element = document.querySelector('{action.selector}');
            element.focus();
            element.value = '{action.value}';
            element.dispatchEvent(new Event('input'));
            """
            self.browser_view.page().runJavaScript(js_code)
            
        self.action_executed.emit(action.action_type, action_data)
        
    def stop_playback(self):
        """Stop playback"""
        self.playing = False

class EmbeddedBrowser(QWidget):
    """Main embedded browser widget with recording capabilities"""
    
    def __init__(self, parent=None, dockable=True):
        super().__init__(parent)
        self.dockable = dockable
        self.recorder = BrowserRecorder()
        self.player = None
        self.request_interceptor = RequestInterceptor()
        
        self.setup_ui()
        self.setup_browser()
        
    def setup_ui(self):
        """Setup the browser UI"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        self.toolbar = QToolBar()
        
        # Navigation controls
        self.back_btn = QPushButton("←")
        self.forward_btn = QPushButton("→")
        self.refresh_btn = QPushButton("↻")
        self.url_bar = QLineEdit()
        self.go_btn = QPushButton("Go")
        
        # Recording controls
        self.record_btn = QPushButton("● Record")
        self.stop_btn = QPushButton("■ Stop")
        self.play_btn = QPushButton("▶ Play")
        self.save_btn = QPushButton("💾 Save")
        self.load_btn = QPushButton("📁 Load")
        
        # Add to toolbar
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.refresh_btn)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.go_btn)
        
        record_layout = QHBoxLayout()
        record_layout.addWidget(self.record_btn)
        record_layout.addWidget(self.stop_btn)
        record_layout.addWidget(self.play_btn)
        record_layout.addWidget(self.save_btn)
        record_layout.addWidget(self.load_btn)
        
        # Browser view
        self.web_view = QWebEngineView()
        self.progress_bar = QProgressBar()
        
        # Status
        self.status_label = QLabel("Ready")
        
        # Layout
        toolbar_widget = QWidget()
        toolbar_layout = QVBoxLayout(toolbar_widget)
        toolbar_layout.addLayout(nav_layout)
        toolbar_layout.addLayout(record_layout)
        toolbar_layout.addWidget(self.progress_bar)
        
        layout.addWidget(toolbar_widget)
        layout.addWidget(self.web_view)
        layout.addWidget(self.status_label)
        
        # Connect signals
        self.connect_signals()
        
    def setup_browser(self):
        """Configure browser settings"""
        profile = QWebEngineProfile.defaultProfile()
        profile.setRequestInterceptor(self.request_interceptor)
        
        # Configure settings
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        
    def connect_signals(self):
        """Connect UI signals"""
        # Navigation
        self.back_btn.clicked.connect(self.web_view.back)
        self.forward_btn.clicked.connect(self.web_view.forward)
        self.refresh_btn.clicked.connect(self.web_view.reload)
        self.go_btn.clicked.connect(self.navigate)
        self.url_bar.returnPressed.connect(self.navigate)
        
        # Recording
        self.record_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.play_btn.clicked.connect(self.start_playback)
        self.save_btn.clicked.connect(self.save_recording)
        self.load_btn.clicked.connect(self.load_recording)
        
        # Browser events
        self.web_view.loadProgress.connect(self.progress_bar.setValue)
        self.web_view.urlChanged.connect(self.url_changed)
        self.web_view.loadFinished.connect(self.load_finished)
        
    def navigate(self):
        """Navigate to URL in address bar"""
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        self.web_view.load(QUrl(url))
        
        if self.recorder.recording:
            self.recorder.record_action('navigate', url=url)
            
    def url_changed(self, url):
        """Handle URL change"""
        self.url_bar.setText(url.toString())
        
    def load_finished(self, success):
        """Handle page load completion"""
        if success:
            self.status_label.setText("Page loaded successfully")
            # Inject recording JavaScript
            if self.recorder.recording:
                self.inject_recording_scripts()
        else:
            self.status_label.setText("Failed to load page")
            
    def inject_recording_scripts(self):
        """Inject JavaScript for recording interactions"""
        js_code = """
        // Add click recording
        document.addEventListener('click', function(e) {
            window.recordAction('click', {
                selector: getSelector(e.target),
                coordinates: [e.clientX, e.clientY]
            });
        });
        
        // Add input recording  
        document.addEventListener('input', function(e) {
            if (e.target.type === 'text' || e.target.type === 'email' || e.target.type === 'password') {
                window.recordAction('type', {
                    selector: getSelector(e.target),
                    value: e.target.value
                });
            }
        });
        
        // Helper function to get CSS selector
        function getSelector(element) {
            if (element.id) return '#' + element.id;
            if (element.className) return '.' + element.className.split(' ')[0];
            return element.tagName.toLowerCase();
        }
        
        // Recording function (will be handled by Python)
        window.recordAction = function(type, data) {
            // This will be intercepted by Python
            console.log('Action:', type, data);
        };
        """
        
        self.web_view.page().runJavaScript(js_code)
        
    def start_recording(self):
        """Start recording browser actions"""
        self.recorder.start_recording()
        self.request_interceptor.recording = True
        self.record_btn.setText("🔴 Recording")
        self.record_btn.setEnabled(False)
        self.status_label.setText("Recording browser actions...")
        
    def stop_recording(self):
        """Stop recording browser actions"""
        self.recorder.stop_recording()
        self.request_interceptor.recording = False
        self.record_btn.setText("● Record")
        self.record_btn.setEnabled(True)
        self.status_label.setText("Recording stopped")
        
    def start_playback(self):
        """Start playing back recorded actions"""
        if not self.recorder.actions:
            self.status_label.setText("No actions to play back")
            return
            
        self.player = BrowserPlayer(self.web_view, self.recorder.actions)
        self.player.action_executed.connect(self.on_action_executed)
        self.player.playback_finished.connect(self.on_playback_finished)
        self.player.start()
        
        self.play_btn.setEnabled(False)
        self.status_label.setText("Playing back recorded actions...")
        
    def on_action_executed(self, action_type, action_data):
        """Handle action execution during playback"""
        self.status_label.setText(f"Executed: {action_type}")
        
    def on_playback_finished(self):
        """Handle playback completion"""
        self.play_btn.setEnabled(True)
        self.status_label.setText("Playback completed")
        
    def save_recording(self):
        """Save recorded actions to file"""
        # Implementation for file dialog and saving
        filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.recorder.save_recording(filename)
        self.status_label.setText(f"Recording saved to {filename}")
        
    def load_recording(self):
        """Load recorded actions from file"""
        # Implementation for file dialog and loading
        # For now, just a placeholder
        self.status_label.setText("Load recording functionality to be implemented")

class BrowserTabWidget(QTabWidget):
    """Tab widget for multiple browser instances"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        
        # Add first tab
        self.add_new_tab()
        
    def add_new_tab(self, url="about:blank"):
        """Add new browser tab"""
        browser = EmbeddedBrowser()
        index = self.addTab(browser, "New Tab")
        self.setCurrentIndex(index)
        
        # Connect to update tab title
        browser.web_view.titleChanged.connect(
            lambda title: self.setTabText(index, title[:20] + "..." if len(title) > 20 else title)
        )
        
        return browser
        
    def close_tab(self, index):
        """Close browser tab"""
        if self.count() > 1:
            self.removeTab(index)

class BrowserDockWidget(QDockWidget):
    """Dockable browser widget"""
    
    def __init__(self, title="Browser", parent=None):
        super().__init__(title, parent)
        self.browser_tabs = BrowserTabWidget()
        self.setWidget(self.browser_tabs)
        
        # Configure dock widget
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                           Qt.DockWidgetArea.RightDockWidgetArea |
                           Qt.DockWidgetArea.BottomDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                        QDockWidget.DockWidgetFeature.DockWidgetClosable |
                        QDockWidget.DockWidgetFeature.DockWidgetFloatable)
