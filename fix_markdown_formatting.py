#!/usr/bin/env python3
"""
Markdown Formatter and Fixer
Automatically fixes common markdown formatting issues across the repository
"""

import os
import re
from pathlib import Path
from typing import List


def fix_markdown_formatting(content: str) -> str:
    """Fix common markdown formatting issues"""
    
    # Fix heading spacing
    content = re.sub(r'^(#{1,6})\s*(.+)$', r'\1 \2', content, flags=re.MULTILINE)
    
    # Ensure blank lines around headings
    content = re.sub(r'^(#{1,6}.+)$', r'\n\1\n', content, flags=re.MULTILINE)
    
    # Fix list spacing
    content = re.sub(r'^(\s*[-*+].*)\n(?!\s*[-*+]|\n)', r'\1\n\n', content, flags=re.MULTILINE)
    
    # Fix code block spacing
    content = re.sub(r'^```', r'\n```', content, flags=re.MULTILINE)
    content = re.sub(r'^```(.+)$', r'```\1\n', content, flags=re.MULTILINE)
    
    # Remove trailing spaces
    content = re.sub(r' +$', '', content, flags=re.MULTILINE)
    
    # Remove trailing punctuation from headings
    content = re.sub(r'^(#{1,6}\s+.+)[.!:]+$', r'\1', content, flags=re.MULTILINE)
    
    # Ensure proper table formatting
    content = re.sub(r'^\|(.+)\|$', r'| \1 |', content, flags=re.MULTILINE)
    
    # Fix excessive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Fix line breaks around horizontal rules
    content = re.sub(r'^---+$', r'\n---\n', content, flags=re.MULTILINE)
    
    return content.strip() + '\n'


def fix_markdown_file(file_path: Path) -> bool:
    """Fix a single markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        fixed_content = fix_markdown_formatting(original_content)
        
        if original_content != fixed_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"📄 No changes needed: {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def find_markdown_files(root_dir: Path) -> List[Path]:
    """Find all markdown files in the repository"""
    md_files = []
    for file_path in root_dir.rglob("*.md"):
        if not any(exclude in str(file_path) for exclude in ['.git', 'node_modules', '.venv']):
            md_files.append(file_path)
    return md_files


def main():
    """Main function to fix all markdown files"""
    print("🔧 Markdown Formatter and Fixer")
    print("=" * 40)
    
    root_dir = Path(".")
    md_files = find_markdown_files(root_dir)
    
    print(f"Found {len(md_files)} markdown files")
    
    fixed_count = 0
    for md_file in md_files:
        if fix_markdown_file(md_file):
            fixed_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {len(md_files)}")
    print(f"   Files fixed: {fixed_count}")
    print(f"   Files unchanged: {len(md_files) - fixed_count}")
    
    if fixed_count > 0:
        print("✅ Markdown formatting complete!")
    else:
        print("✨ All markdown files were already properly formatted!")


if __name__ == "__main__":
    main()
