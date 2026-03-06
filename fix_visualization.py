#!/usr/bin/env python3
"""
Ensure graph visualization appears right after graph = builder.compile() in all notebooks.
Remove duplicates and place visualization in the correct position.
"""

import json
from pathlib import Path

VISUALIZATION_CODE = """from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))"""

def has_visualization_code(source_text):
    """Check if source contains visualization code."""
    return 'draw_mermaid_png' in source_text or ('get_graph()' in source_text and 'display' in source_text)

def find_compile_cell_index(cells):
    """Find the cell with graph = builder.compile()."""
    for i, cell in enumerate(cells):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if 'builder.compile()' in source and 'graph' in source:
                return i
    return -1

def fix_visualization(notebook_path):
    """Ensure visualization is right after compile, remove duplicates."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    compile_idx = find_compile_cell_index(nb['cells'])
    if compile_idx == -1:
        print(f"  ⊘ No compile() found: {notebook_path.name}")
        return False
    
    # Find all cells with visualization
    viz_cells = []
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if has_visualization_code(source):
                viz_cells.append(i)
    
    # Check if we need to make changes
    has_viz_after_compile = (compile_idx + 1) in viz_cells
    has_duplicates = len(viz_cells) > 1
    needs_viz = len(viz_cells) == 0
    
    if has_viz_after_compile and not has_duplicates:
        print(f"  ✓ Already correct: {notebook_path.name}")
        return False
    
    modified = False
    
    # Remove all existing visualization cells
    if viz_cells:
        for idx in reversed(viz_cells):  # Remove from end to preserve indices
            del nb['cells'][idx]
            modified = True
            # Adjust compile_idx if we removed cells before it
            if idx <= compile_idx:
                compile_idx -= 1
    
    # Create new visualization cell
    viz_cell = {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': VISUALIZATION_CODE.split('\n')
    }
    
    # Insert right after compile
    nb['cells'].insert(compile_idx + 1, viz_cell)
    modified = True
    
    # Write back
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    
    action = "Fixed positioning" if has_duplicates else "Added visualization"
    print(f"  ✓ {action}: {notebook_path.name}")
    return True

def main():
    tutorial_path = Path('/home/navinkumar_25_gmail_com/langraph_tutorial')
    
    target_notebooks = [
        'Lesson_01_First_Graph.ipynb',
        'Lesson_02_Multiple_Nodes.ipynb',
        'Lesson_03_Conditional_Routing.ipynb',
        'Lesson_04_Reducers.ipynb',
        'Lesson_05_Loops_Validation.ipynb',
        'Lesson_10_MapReduce_Numbers.ipynb',
        'Lesson_11_Subgraph_Architecture.ipynb',
        'Lesson_12_MultiAgent_Supervisor_Worker.ipynb',
        'Lesson_13_ShortTerm_Memory.ipynb',
        'Lesson_14_Message_Trimming_Summarization.ipynb',
        'Lesson_15_LongTerm_Memory.ipynb',
        'Lesson_16_Streaming_Responses.ipynb',
        'Lesson_20_Self_Critique.ipynb',
    ]
    
    print("\nFixing graph visualization positioning in notebooks...\n")
    
    updated_count = 0
    for notebook_name in target_notebooks:
        notebook_path = tutorial_path / notebook_name
        if notebook_path.exists():
            if fix_visualization(notebook_path):
                updated_count += 1
    
    print(f"\n✓ Updated {updated_count} notebooks")
    return updated_count

if __name__ == '__main__':
    main()
