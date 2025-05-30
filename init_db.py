import logging
from app import app, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    with app.app_context():
        logger.info("Starting database initialization...")
        db.create_all()
        logger.info("Database tables created successfully!")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise 