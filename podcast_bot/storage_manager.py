"""
storage_manager.py

A utility module for handling file system operations.
- Downloads remote files (video/music backgrounds).
- Manages creation and cleanup of temporary directories for each show run.
- Deletes generated media files after they are no longer needed.
"""

import os
import shutil
import logging
import requests
from pathlib import Path
from typing import Optional

import config


class StorageManager:
    """Manages file downloads, temporary directories, and cleanup."""

    def __init__(self, show_id: str):
        """
        Initializes the StorageManager for a specific show run.

        Args:
            show_id (str): A unique identifier for the current show run.
        """
        self.logger = logging.getLogger(__name__)
        self.show_id = show_id

        # Define specific directories for this show run
        self.show_audio_dir = config.AUDIO_DIR / self.show_id
        self.show_subtitles_dir = config.SUBTITLES_DIR / self.show_id
        self.show_video_dir = config.VIDEO_DIR / self.show_id
        self.show_parts_dir = config.PARTS_DIR / self.show_id

        # Local paths for downloaded background media
        self.background_video_path = config.TEMP_DIR / "background.mp4"
        self.background_music_path = config.TEMP_DIR / "background.mp3"

    def create_show_directories(self):
        """Creates all necessary temporary directories for the current show run."""
        self.logger.info(f"[{self.show_id}] Creating temporary directories for show.")
        dirs_to_create = [
            self.show_audio_dir,
            self.show_subtitles_dir,
            self.show_video_dir,
            self.show_parts_dir
        ]
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {dir_path}")

    def download_background_media(self) -> None:
        """
        Downloads background video and music if they don't already exist.
        This avoids re-downloading large files for every show.
        """
        self.logger.info("Checking for background media files...")
        self._download_file(config.BACKGROUND_VIDEO_URL, self.background_video_path)
        self._download_file(config.BACKGROUND_MUSIC_URL, self.background_music_path)

    def _download_file(self, url: str, local_path: Path) -> None:
        """Helper to download a file from a URL if it doesn't exist locally."""
        if local_path.exists():
            self.logger.info(f"File already exists, skipping download: {local_path}")
            return

        self.logger.info(f"Downloading from {url} to {local_path}...")
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            self.logger.info(f"Successfully downloaded {local_path.name}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download {url}. Error: {e}")
            raise IOError(f"Could not download required media from {url}") from e

    def cleanup_show_media(self) -> None:
        """
        Deletes all temporary files and directories associated with the current show run.
        This should be called after the final part has been posted.
        """
        self.logger.warning(f"[{self.show_id}] --- INITIATING FULL CLEANUP ---")

        # Directories to remove for this specific show
        dirs_to_delete = [
            self.show_audio_dir,
            self.show_subtitles_dir,
            self.show_video_dir,
            self.show_parts_dir
        ]

        for dir_path in dirs_to_delete:
            self._safe_delete(dir_path)

        # Also remove the master audio and video files from the parent temp dirs
        master_audio = config.AUDIO_DIR / f"master_audio_{self.show_id}.wav"
        master_video = config.VIDEO_DIR / f"final_show_video_{self.show_id}.mp4"
        final_subs = config.SUBTITLES_DIR / f"subtitles_{self.show_id}.srt"

        self._safe_delete(master_audio)
        self._safe_delete(master_video)
        self._safe_delete(final_subs)

        self.logger.info(f"[{self.show_id}] --- FULL CLEANUP COMPLETE ---")

    def cleanup_posted_part(self, part_path: str) -> None:
        """
        Deletes a specific video part file after it has been successfully posted.

        Args:
            part_path (str): The full path to the video part file.
        """
        self.logger.info(f"[{self.show_id}] Cleaning up posted part: {part_path}")
        self._safe_delete(Path(part_path))

    def _safe_delete(self, path: Path) -> None:
        """Safely deletes a file or directory, logging the outcome."""
        try:
            if not path.exists():
                self.logger.debug(f"Attempted to delete non-existent path: {path}")
                return

            if path.is_dir():
                shutil.rmtree(path)
                self.logger.info(f"Successfully deleted directory: {path}")
            else:
                os.remove(path)
                self.logger.info(f"Successfully deleted file: {path}")

        except (OSError, shutil.Error) as e:
            self.logger.error(f"Error during cleanup of {path}. Error: {e}")
            # In a production system, you might want to flag this for manual review.