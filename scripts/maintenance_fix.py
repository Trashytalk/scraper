#!/usr/bin/env python3
"""
Code Maintenance Tool - Fix Critical Issues
"""
import re
from pathlib import Path


def fix_qt_event_handlers(file_path: Path):
    """Fix Qt event handler parameter names to match base class signatures."""
    content = file_path.read_text(encoding="utf-8")

    # Fix common Qt event handler parameter names
    fixes = [
        (r"def paintEvent\(self, event\):", "def paintEvent(self, a0):"),
        (r"def mousePressEvent\(self, event\):", "def mousePressEvent(self, a0):"),
        (r"def mouseMoveEvent\(self, event\):", "def mouseMoveEvent(self, a0):"),
        (r"def wheelEvent\(self, event\):", "def wheelEvent(self, a0):"),
        (r"def closeEvent\(self, event: Any\)", "def closeEvent(self, a0: Any)"),
        (r"def leaveEvent\(self, event\):", "def leaveEvent(self, a0):"),
        (r"def enterEvent\(self, event\):", "def enterEvent(self, a0):"),
    ]

    modified = False
    for pattern, replacement in fixes:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            modified = True
            print(f"Fixed event handler in {file_path}: {pattern}")

    # Also fix the parameter usage inside methods
    content = re.sub(r"super\(\)\.(\w+Event)\(event\)", r"super().\1(a0)", content)

    if modified:
        file_path.write_text(content, encoding="utf-8")
        print(f"✅ Fixed event handlers in {file_path}")

    return modified


def fix_qt_imports(file_path: Path):
    """Fix common Qt import issues."""
    content = file_path.read_text(encoding="utf-8")

    # Fix Qt widget imports
    fixes = [
        (
            r"from PyQt6 import QtWidgets",
            "from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication",
        ),
        (r"QtWidgets\.QDockWidgetArea", "Qt.DockWidgetArea"),
        (r"QtWidgets\.QMainWindow", "QMainWindow"),
    ]

    modified = False
    for pattern, replacement in fixes:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            modified = True
            print(f"Fixed import in {file_path}: {pattern}")

    if modified:
        file_path.write_text(content, encoding="utf-8")
        print(f"✅ Fixed imports in {file_path}")

    return modified


def main():
    """Run maintenance fixes on critical files."""
    script_dir = Path(__file__).parent
    gui_components = script_dir / "gui" / "components"

    critical_files = [
        "tooltip_system.py",
        "data_visualization.py",
        "dashboard.py",
        "embedded_browser.py",
    ]

    print("🔧 Starting Critical Issue Maintenance...")
    print("=" * 50)

    for filename in critical_files:
        file_path = gui_components / filename
        if file_path.exists():
            print(f"\\n📁 Processing {filename}")

            # Fix Qt event handlers
            fix_qt_event_handlers(file_path)

            # Fix Qt imports
            fix_qt_imports(file_path)

        else:
            print(f"⚠️  File not found: {file_path}")

    print("\\n" + "=" * 50)
    print("✅ Critical maintenance completed!")
    print("\\n🔍 Next steps:")
    print("1. Run integration test to verify fixes")
    print("2. Install code quality tools: pip install mypy black isort flake8")
    print("3. Set up pre-commit hooks for automated checks")


if __name__ == "__main__":
    main()
