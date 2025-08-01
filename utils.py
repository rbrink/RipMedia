import subprocess
import logging
from logging.handlers import RotatingFileHandler

class DiscUtils:
    @staticmethod
    def is_disc_inserted():
        """Check if a disc is inserted in the drive."""
        try:
            result = subprocess.run(['wmic', 'cdrom', 'get', 'MediaLoaded'], capture_output=True, text=True)
            return "TRUE" in result.stdout
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to check disc status: {e}")
            return False

class Logger:
    @staticmethod
    def get_logger(name, log_file="./logs/app.log", level=logging.DEBUG):
        """Configure and return a logger instance."""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Check if handlers are already added to avoid duplicate logs
        if not logger.handlers:
            # Create file handler with rotation
            file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
            file_handler.setLevel(level)
            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            # Define log format
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            # Add handlers to logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        return logger
