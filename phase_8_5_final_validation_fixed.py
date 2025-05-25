#!/usr/bin/env python3
"""
Phase 8.5 Final Validation - Unicode Safe Version
Fixed all Unicode handling issues for proper cleanup
"""

import sys
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class UnicodeAwareJSONEncoder(json.JSONEncoder):
    """JSON encoder that properly handles Unicode characters"""
    
    def encode(self, obj):
        """Encode with proper Unicode handling"""
        try:
            return super().encode(obj)
        except UnicodeEncodeError:
            # Fallback to ASCII-safe encoding
            return json.dumps(obj, ensure_ascii=True, default=str)

def safe_write_json(data, filepath):
    """Safely write JSON with Unicode handling"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, cls=UnicodeAwareJSONEncoder)
        return True
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        logger.warning(f"Unicode issue writing {filepath}: {e}")
        # Fallback to ASCII-safe version
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=True, default=str)
            return True
        except Exception as e2:
            logger.error(f"Failed to write {filepath}: {e2}")
            return False

def safe_print(text):
    """Safely print text with Unicode handling"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback to ASCII representation
        print(text.encode('ascii', 'replace').decode('ascii'))
