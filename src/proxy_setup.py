import os
import httpx
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging to capture information and errors for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_http_client_with_proxy():
    proxy = os.getenv('PROXY')
    http_client = None
    if proxy:
        try:
            # Create an HTTP client using the provided proxy settings
            http_client = httpx.Client(proxies={'http://': proxy, 'https://': proxy})
            logger.info("Proxy setup successful.")
        except Exception as e:
            logger.error(f"Error during proxy setup: {e}")
            http_client = None
    else:
        logger.info("No proxy configuration found in environment variables.")
    return http_client