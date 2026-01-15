"""
scheduler.py

The main orchestrator of the AI Radio Show Bot.
- Initializes all engine and manager components.
- Defines the main `run_show_cycle` function that handles the A-to-Z process of creating a show.
- Uses a scheduling library to run the cycle at a fixed interval.
"""

import time
import logging
from datetime import datetime

import schedule

import config
from character_manager import CharacterManager
from show_engine import ShowEngine
from voice_engine import VoiceEngine
from subtitle_engine import SubtitleEngine
from video_engine import VideoEngine
from posting_engine import PostingEngine
from storage_manager import StorageManager

# --- Global Component Initialization ---
# These are initialized once to be reused in each cycle.
# This is crucial for performance, especially for the VoiceEngine which loads large models.
try:
    logger = logging.getLogger(__name__)

    logger.info("--- Initializing All System Components ---")

    # Core data and content managers
    character_manager = CharacterManager()
    show_engine = ShowEngine(character_manager)

    # Media generation engines
    voice_engine = VoiceEngine(character_manager)
    subtitle_engine = SubtitleEngine()

    logger.info("--- All Components Initialized Successfully ---")

except Exception as e:
    # If any core component fails to initialize, the application cannot run.
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT,
        handlers=[logging.StreamHandler()]  # Log to console if file logger fails
    )
    logging.critical(f"FATAL: A critical component failed to initialize: {e}", exc_info=True)
    # Exit with a non-zero code to indicate failure, useful for process managers like systemd.
    exit(1)


def run_show_cycle():
    """
    Executes one complete cycle of show generation, processing, and posting.
    This function is designed to be robust and handle errors within a single cycle
    without crashing the entire application.
    """
    show_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"####################################################")
    logger.info(f"### STARTING NEW SHOW CYCLE | ID: {show_id} ###")
    logger.info(f"####################################################")

    # A single StorageManager instance is created per show cycle.
    storage_manager = StorageManager(show_id)

    try:
        # 1. Setup: Create directories and download media if needed
        storage_manager.create_show_directories()
        storage_manager.download_background_media()  # Idempotent

        # 2. Pre-production: Select characters and generate script
        participants = character_manager.select_show_participants()
        hosts = participants['hosts']
        guests = participants['guests']

        script = show_engine.generate_script(hosts, guests, show_id)
        if not script:
            raise ValueError("Script generation returned an empty script.")

        # 3. Production: Generate all media assets
        master_audio_path, _ = voice_engine.generate_show_audio(script, show_id)
        subtitle_path = subtitle_engine.generate_subtitles(master_audio_path, show_id)

        # The VideoEngine needs its own StorageManager to know the paths
        video_engine = VideoEngine(storage_manager)
        final_video_path = video_engine.assemble_video(master_audio_path, subtitle_path)

        # 4. Post-production: Split video into parts
        video_parts = video_engine.split_video_into_parts(final_video_path)
        if not video_parts:
            logger.warning(f"[{show_id}] No video parts were created. Skipping posting.")
            return  # End the cycle here

        # 5. Distribution: Post parts to social media
        posting_engine = PostingEngine(storage_manager)
        posting_engine.post_all_parts(video_parts, hosts, guests)

        logger.info(f"[{show_id}] --- SHOW CYCLE COMPLETED SUCCESSFULLY ---")

    except Exception as e:
        logger.critical(f"[{show_id}] A critical error occurred during the show cycle: {e}", exc_info=True)
        logger.error(f"[{show_id}] The show cycle was aborted. The system will wait for the next scheduled run.")
        # The 'finally' block will ensure cleanup still happens.

    finally:
        # 6. Cleanup: Remove all temporary files for this show ID
        logger.info(f"[{show_id}] Initiating final cleanup for the show cycle.")
        storage_manager.cleanup_show_media()
        logger.info(f"[{show_id}] Cycle cleanup complete.")


def start_scheduler():
    """
    Starts the main scheduling loop for the bot.
    """
    logger.info("Scheduler starting. Bot is now in its main execution loop.")
    logger.info(f"A new show cycle will run every {config.SHOW_INTERVAL_SECONDS} seconds.")

    # Schedule the job.
    schedule.every(config.SHOW_INTERVAL_SECONDS).seconds.do(run_show_cycle)

    # Run the first job immediately, then wait for the schedule.
    logger.info("Executing the first show cycle immediately upon startup.")
    run_show_cycle()

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.warning("Shutdown signal received. Exiting scheduler loop.")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred in the scheduler loop: {e}", exc_info=True)
            # Sleep for a bit before retrying to prevent rapid-fire error loops
            time.sleep(60)