#!/usr/bin/env python3
"""
Simple launcher for the Real-Time Audio FX application.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Now import and run the main function
from main import main

if __name__ == "__main__":
    main()