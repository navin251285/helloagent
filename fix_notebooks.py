#!/usr/bin/env python3
"""
Fix notebooks by converting commented markdown in code cells to proper markdown cells.
"""

import json
from pathlib import Path


def extract_markdown_and_code(cell_source):
    """Extract commented markdown and remaining code from a cell."""
    source_str = ''.join(cell_source) if isinstance(cell_source, list) else cell_source
    lines = source_str.split('\n')
    
    markdown_lines = []
    code_lines = []
    in_markdown = True
    
    for line in lines:
        stripped = line.lstrip()
        
        # Lines starting with # are comments/markdown
        if stripped.startswith('#'):
            if in_markdown:
                # Extract markdown content after #
                if stripped == '#':
                    markdown_lines.append('')
                else:
                    # Remove # and handle both '# text' and '#text'
                    content = stripped[1:].lstrip() if stripped.startswith('# ') else stripped[1:]
                    markdown_lines.append(content)
        elif stripped == '':
            # Empty line
            if in_markdown:
                markdown_lines.append('')
            else:
                code_lines.append(line)
        else:
            # Non-comment line = code starts
            in_markdown = False
            code_lines.append(line)
    
    # Clean up markdown: remove trailing empty lines
    while markdown_lines and markdown_lines[-1] == '':
        markdown_lines.pop()
    
    # Clean up code: remove leading empty lines
    while code_lines and code_lines[0].strip() == '':
        code_lines.pop(0)
    
    markdown_text = '\n'.join(markdown_lines)
    code_text = '\n'.join(code_lines)
    
    return markdown_text, code_text


def should_convert(cell_source):
    """Check if code cell starts with commented content."""
    source_str = ''.join(cell_source) if isinstance(cell_source, list) else cell_source
    first_line = source_str.lstrip().split('\n')[0] if source_str else ''
    return first_line.startswith('#')


def fix_notebook(notebook_path):
    """Convert commented markdown in code cells to markdown cells."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    new_cells = []
    modified = False
    
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code' and should_convert(cell['source']):
            # This code cell has commented-out markdown
            markdown_text, code_text = extract_markdown_and_code(cell['source'])
            
            # Add markdown cell if there's markdown content
            if markdown_text.strip():
                new_cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': markdown_text.split('\n')
                })
            
            # Add code cell if there's code content
            if code_text.strip():
                new_cells.append({
                    'cell_type': 'code',
                    'execution_count': cell.get('execution_count'),
                    'metadata': cell.get('metadata', {}),
                    'outputs': cell.get('outputs', []),
                    'source': code_text.split('\n')
                })
            
            modified = True
        else:
            # Keep cell as-is
            new_cells.append(cell)
    
    if modified:
        notebook['cells'] = new_cells
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        return True
    return False


def main():
    tutorial_path = Path('/home/navinkumar_25_gmail_com/agentic_ai_tutorial')
    notebooks = sorted(tutorial_path.glob('Lesson_*.ipynb'))
    
    print(f"Fixing {len(notebooks)} notebooks...\n")
    fixed_count = 0
    
    for notebook_path in notebooks:
        if fix_notebook(str(notebook_path)):
            fixed_count += 1
            print(f"✓ {notebook_path.name}")
    
    print(f"\n✓ Fixed {fixed_count}/{len(notebooks)} notebooks")


if __name__ == '__main__':
    main()
