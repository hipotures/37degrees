#!/usr/bin/env python3
"""
Hook that handles stdin line by line
"""

import sys

if __name__ == "__main__":
    try:
        # Read all available lines without blocking
        lines = []
        for line in sys.stdin:
            lines.append(line)
    except EOFError:
        pass
    except Exception:
        pass
    
    sys.exit(0)