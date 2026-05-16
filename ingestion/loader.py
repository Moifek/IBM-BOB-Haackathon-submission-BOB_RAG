"""
Data loader for ingestion pipeline.

Loads chunked medical content from JSONL files.
"""
import json
from typing import List, Dict, Optional


def load_chunks(path: str, limit: Optional[int] = None) -> List[Dict]:
    """
    Load chunks from a JSONL file.
    
    Each line in the JSONL file should be a JSON object with:
    - content: The text content of the chunk
    - metadata: Dictionary with metadata (title, source, etc.)
    
    Args:
        path: Path to the JSONL file (e.g., data/statpearls_chunks.jsonl)
        limit: Optional limit on number of chunks to load (for testing)
    
    Returns:
        List of dicts with 'content' and 'metadata' fields
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If a line contains invalid JSON
    """
    chunks = []
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Skip empty lines
                line = line.strip()
                if not line:
                    continue
                
                try:
                    chunk = json.loads(line)
                    
                    # Validate required fields
                    if 'content' not in chunk:
                        raise ValueError(f"Line {line_num}: Missing 'content' field")
                    if 'metadata' not in chunk:
                        chunk['metadata'] = {}
                    
                    chunks.append(chunk)
                    
                    # Check limit
                    if limit is not None and len(chunks) >= limit:
                        break
                        
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"Line {line_num}: {e.msg}",
                        e.doc,
                        e.pos
                    )
                except ValueError as e:
                    raise ValueError(f"Line {line_num}: {str(e)}")
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found: {path}")
    
    return chunks

# Made with Bob