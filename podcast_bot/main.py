"""
main.py

The main entry point for the AI Radio Show Bot application.
- Sets up system-wide logging.
- Initializes and starts the show scheduler.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

import config
from scheduler import start_scheduler


def setup_logging():
    """
    Configures the global logger for the application.
    - Logs to both a file and the console.
    - Uses a rotating file handler to prevent log files from growing indefinitely.
    """
    # Create a logger instance
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)

    # Create a formatter
    formatter = logging.Formatter(config.LOG_FORMAT)

    # Create a rotating file handler
    # This will create up to 5 log files, each up to 5MB in size.
    # When the current log file reaches 5MB, it's renamed (e.g., to .1, .2)
    # and a new file is started. This prevents a single log file from
    # becoming excessively large.
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    # Create a stream handler to also log to the console (useful for `docker logs` or `systemd`)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.info("Logging configured successfully. Logging to file and console.")
    logger.info(f"Log level set to: {config.LOG_LEVEL}")

    # Capture unhandled exceptions with the logger
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception


def main():
    """
    Main function to start the bot.
    """
    print("=========================================")
    print("===   AI Radio Show Bot Initializing  ===")
    print("=========================================")

    setup_logging()

    # The main logic is handed off to the scheduler
    try:
        start_scheduler()
    except Exception as e:
        # This will catch errors during the initial component setup in scheduler.py
        logging.getLogger().critical(
            "A fatal error occurred during initialization before the scheduler could start.",
            exc_info=True
        )
        sys.exit(1)  # Exit with error code

    print("=========================================")
    print("===    AI Radio Show Bot Shut Down    ===")
    print("=========================================")
    logging.getLogger().info("Application has shut down gracefully.")


if __name__ == "__main__":
    # This block ensures the main function is called only when the script is executed directly
    main()