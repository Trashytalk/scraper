#!/usr/bin/env python3
"""
Production Cleanup Script
Removes debug code, console.log statements, and development artifacts
"""

import os
import re
import glob
from pathlib import Path

def cleanup_debug_patterns():
    """Remove debug patterns from codebase"""
    
    # Patterns to remove or replace
    debug_patterns = [
        # Console debug statements
        (r'console\.log\("🚨.*?\");?', ''),
        (r'console\.log\("=== MODAL DEBUG.*?\");?', ''),
        (r'console\.log\("DEBUG:.*?\");?', ''),
        (r'print\(f?"DEBUG:.*?\)', ''),
        
        # Debug styling
        (r'backgroundColor: "rgba\(255,0,0,0\.9\)".*?// Changed to red for debugging', 'backgroundColor: "rgba(0,0,0,0.5)"'),
        
        # Debug flags
        (r'DEBUG\s*=\s*[tT]rue', 'DEBUG=false'),
        (r'debug_mode\s*=\s*[tT]rue', 'debug_mode=false'),
        
        # Test/debug comments
        (r'# DEBUG.*?\n', ''),
        (r'// DEBUG.*?\n', ''),
    ]
    
    files_to_clean = []
    
    # Find files to clean
    for pattern in ['**/*.py', '**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx', '**/*.sh']:
        files_to_clean.extend(glob.glob(pattern, recursive=True))
    
    cleaned_files = []
    
    for file_path in files_to_clean:
        if any(skip in file_path for skip in ['__pycache__', 'node_modules', '.git', 'htmlcov']):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply debug pattern replacements
            for pattern, replacement in debug_patterns:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            
            # If file was modified, write it back
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                cleaned_files.append(file_path)
                
        except Exception as e:
            print(f"Warning: Could not process {file_path}: {e}")
    
    return cleaned_files

def remove_debug_files():
    """Remove dedicated debug/test files that shouldn't be in production"""
    debug_files = [
        'test_modal_debug.py',
        'debug_frontend_data.py', 
        'debug_crawling.py',
        'test_job_lifecycle.py',
        'demo_working_crawling.py',
        'quick_error_test.py',
        'test_*.py'  # Test files that start with test_
    ]
    
    removed_files = []
    
    for pattern in debug_files:
        for file_path in glob.glob(pattern):
            if os.path.exists(file_path):
                # Move to archive instead of deleting
                archive_dir = 'archived_debug_files'
                os.makedirs(archive_dir, exist_ok=True)
                os.rename(file_path, os.path.join(archive_dir, os.path.basename(file_path)))
                removed_files.append(file_path)
    
    return removed_files

def optimize_production_config():
    """Update configuration files for production"""
    config_updates = {
        'docker-compose.yml': [
            ('DEBUG=true', 'DEBUG=false'),
            ('LOG_LEVEL=DEBUG', 'LOG_LEVEL=INFO'),
        ],
        'backend_server.py': [
            ('reload=True', 'reload=False'),
            ('debug=True', 'debug=False'),
        ],
        '.env': [
            ('DEBUG=true', 'DEBUG=false'),
            ('LOG_LEVEL=DEBUG', 'LOG_LEVEL=INFO'),
        ]
    }
    
    updated_files = []
    
    for file_path, replacements in config_updates.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                original_content = content
                for old, new in replacements:
                    content = content.replace(old, new)
                
                if content != original_content:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    updated_files.append(file_path)
                    
            except Exception as e:
                print(f"Warning: Could not update {file_path}: {e}")
    
    return updated_files

if __name__ == "__main__":
    print("🧹 Production Cleanup Script")
    print("=" * 50)
    
    # Clean debug patterns
    print("🔍 Cleaning debug patterns...")
    cleaned_files = cleanup_debug_patterns()
    if cleaned_files:
        print(f"   ✅ Cleaned {len(cleaned_files)} files")
        for f in cleaned_files[:5]:  # Show first 5
            print(f"      - {f}")
        if len(cleaned_files) > 5:
            print(f"      ... and {len(cleaned_files) - 5} more")
    else:
        print("   ✅ No debug patterns found")
    
    # Archive debug files
    print("\n📁 Archiving debug files...")
    removed_files = remove_debug_files()
    if removed_files:
        print(f"   ✅ Archived {len(removed_files)} debug files to archived_debug_files/")
        for f in removed_files:
            print(f"      - {f}")
    else:
        print("   ✅ No debug files to archive")
    
    # Update production configs
    print("\n⚙️ Optimizing production configuration...")
    updated_files = optimize_production_config()
    if updated_files:
        print(f"   ✅ Updated {len(updated_files)} config files")
        for f in updated_files:
            print(f"      - {f}")
    else:
        print("   ✅ Production config already optimized")
    
    print("\n🎉 Production cleanup complete!")
    print("\n📋 Manual tasks to complete:")
    print("   1. Review archived debug files before deleting")
    print("   2. Test the application after cleanup")
    print("   3. Update environment variables for production")
    print("   4. Enable security headers and HTTPS")
    print("   5. Configure monitoring and logging")
