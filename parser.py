import os
import re
from typing import List, Dict, Optional

def parse_abc_file(file_path: str) -> List[Dict]:
    """
    Parses a single .abc file and extracts tunes.
    
    Args:
        file_path (str): The path to the .abc file.
        
    Returns:
        List[Dict]: A list of dictionaries, where each dict is a tune.
    """
    tunes = []
    current_tune = {}
    in_tune = False
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for the start of a tune (X: is the index field)
            if line.startswith('X:'):
                if current_tune:
                    tunes.append(current_tune)
                current_tune = {'content': ''} # Reset for new tune
                in_tune = True
                
            # Extract headers (T: Title, M: Meter, K: Key, R: Type/Rhythm)
            if in_tune:
                # Store the raw line in content
                current_tune['content'] += line + '\n'
                
                # Parse specific fields
                if line.startswith('T:'):
                    # Only take the first title if multiple exist
                    if 'title' not in current_tune:
                        current_tune['title'] = line[2:].strip()
                elif line.startswith('M:'):
                    current_tune['meter'] = line[2:].strip()
                elif line.startswith('K:'):
                    current_tune['key'] = line[2:].strip()
                elif line.startswith('R:'):
                    current_tune['type'] = line[2:].strip()
        
        # Append the last tune found in the file
        if current_tune:
            tunes.append(current_tune)
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        
    return tunes