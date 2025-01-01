from .app import run as run_bot
from .voice_assistant import run as run_voice
from multiprocessing import Process
from botify.logging.logger import logger
import time

import argparse

def main():
    parser = argparse.ArgumentParser(description="Run the Botify services")
    parser.add_argument('--dev', action='store_true', help='Run in development mode')
    args = parser.parse_args()

    logger.info("Starting botify services")
    if args.dev:
        logger.info("Running in development mode")

    # Create separate processes for bot and voice assistant
    bot_process = Process(target=run_bot)
    voice_process = Process(target=run_voice, args=(args.dev,))
    
    # Start both processes
    bot_process.start()
    voice_process.start()
        
    try:
        # Keep the main process alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down botify services")
        # Terminate processes gracefully
        bot_process.terminate()
        voice_process.terminate()
        
        # Wait for processes to finish
        bot_process.join()
        voice_process.join()
    except Exception as e:
        logger.error(f"Error in main process: {e}")
    finally:
        logger.info("Botify services stopped")

if __name__ == "__main__":
    main()
