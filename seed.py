#!/usr/bin/env python3
"""
Docker Seeder Script - Entry point for containerized seeding
Automatically chooses appropriate seeder based on environment
"""

import sys
import os
from decouple import config

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main seeder entry point"""
    # Check if we should use production data or test data
    use_production = config('USE_PRODUCTION_DATA', default=False, cast=bool)
    
    print("=" * 60)
    print("CafePOS Docker Seeder")
    print("=" * 60)
    
    if use_production:
        print("Using production data seeder...")
        from seed_production_data import main as production_main
        production_main()
    else:
        print("Using test data seeder...")
        from seed_test_data import main as test_main
        test_main()

if __name__ == "__main__":
    main()