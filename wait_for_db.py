#!/usr/bin/env python3
"""
Wait for Database to be Ready
Used in Docker Compose to ensure database is ready before running tests
"""

import time
import sys
from sqlalchemy import create_engine
from decouple import config

def wait_for_db(max_retries=30, delay=2):
    """
    Wait for the database to become available
    
    Args:
        max_retries: Maximum number of connection attempts
        delay: Seconds to wait between attempts
    """
    database_url = config('DATABASE_URL')
    
    print(f"Waiting for database at {database_url}")
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url)
            connection = engine.connect()
            connection.close()
            engine.dispose()
            
            print(f"Database is ready! (attempt {attempt + 1})")
            return True
            
        except Exception as e:
            print(f"Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                print("Max retries reached. Database is not available.")
                return False
    
    return False

if __name__ == "__main__":
    if not wait_for_db():
        sys.exit(1)
    print("Database connection successful!")