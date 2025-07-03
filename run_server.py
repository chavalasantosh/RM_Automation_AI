import uvicorn
import sys
import os
import socket
import time
import loggingN
import yaml
from typing import Optional

def load_config() -> dict:
    """Load configuration from config.yaml."""
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return {
            'server': {
                'port': 8001,
                'host': '0.0.0.0',
                'log_level': 'info'
            }
        }

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server.log')
    ]
)
logger = logging.getLogger(__name__)

def is_port_in_use(port: int, host: str = '127.0.0.1') -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

def find_available_port(start_port: int, max_attempts: int = 10) -> Optional[int]:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return None

def main():
    try:
        # Load configuration
        config = load_config()
        server_config = config.get('server', {})
        port = server_config.get('port', 8001)
        host = server_config.get('host', '0.0.0.0')
        log_level = server_config.get('log_level', 'info')

        # Check if port is in use and try to find an available one
        if is_port_in_use(port):
            logger.warning(f"Port {port} is already in use.")
            available_port = find_available_port(port + 1)
            if available_port:
                logger.info(f"Using alternative port: {available_port}")
                port = available_port
            else:
                logger.error("Could not find an available port. Please close any existing servers and try again.")
            sys.exit(1)

        logger.info("\n=== Starting RME Server ===")
        logger.info(f"Server will be available at: http://{host}:{port}")
        logger.info("Press Ctrl+C to stop the server\n")
        
        # Add the current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Try importing main components to check for errors
        try:
            logger.debug("Attempting to import main application...")
            from app.main import app
            logger.debug("Successfully imported main application")
        except ImportError as e:
            logger.error(f"Failed to import main application: {str(e)}")
            logger.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error importing main application: {str(e)}", exc_info=True)
            sys.exit(1)
        
        # Run the server with explicit configuration
        logger.debug("Starting uvicorn server...")
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=True,  # Enable reload for development
            log_level=log_level,
            access_log=True,
            workers=1
        )
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
        sys.exit(0)
    except PermissionError:
        logger.error("\nPermission denied. Please ensure you have proper permissions to run the server.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nError starting server: {str(e)}", exc_info=True)
        logger.error("Please check if:")
        logger.error("1. All required packages are installed (pip install -r requirements.txt)")
        logger.error("2. You have proper permissions to run the server")
        logger.error("3. The configuration file (config.yaml) is valid")
        sys.exit(1)

if __name__ == "__main__":
    main() 