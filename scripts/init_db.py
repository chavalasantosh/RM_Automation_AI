#!/usr/bin/env python3
"""
Database initialization script.
This script will:
1. Create the database directory if it doesn't exist
2. Initialize the database using SQLAlchemy
3. Run any pending migrations using Alembic
"""

import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
parent_dir = str(Path(__file__).parent.parent)
logger.debug(f"Adding {parent_dir} to Python path")
sys.path.append(parent_dir)

try:
    from app.core.database import init_db, DATABASE_URL
    from alembic.config import Config
    from alembic import command
    logger.debug("Successfully imported required modules")
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def main():
    logger.info("Starting database initialization...")
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    logger.debug(f"Checking data directory at {data_dir.absolute()}")
    if not data_dir.exists():
        logger.info(f"Creating data directory at {data_dir.absolute()}")
        data_dir.mkdir(exist_ok=True)
    else:
        logger.debug("Data directory already exists")
    
    logger.info("Initializing database...")
    try:
        # Initialize database
        logger.debug(f"Using database URL: {DATABASE_URL}")
        init_db()
        logger.info("Database initialized successfully")
        
        # Run migrations
        logger.info("Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        logger.debug("Created Alembic config")
        
        # Verify alembic.ini exists and is readable
        if not Path("alembic.ini").exists():
            raise FileNotFoundError("alembic.ini not found")
        logger.debug("Found alembic.ini")
        
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 