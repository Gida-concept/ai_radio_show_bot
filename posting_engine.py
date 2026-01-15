"""
posting_engine.py

Handles publishing video parts to social media platforms (Facebook).
- Constructs post captions.
- Uses the Facebook Graph API for video uploads.
"""

import time
import logging
import requests
from pathlib import Path  # <--- THIS WAS MISSING
from typing import List, Dict

import config

class PostingEngine:
    """Manages the posting of video content to social media."""

    def __init__(self, storage_manager):
        """
        Initializes the PostingEngine.

        Args:
            storage_manager (StorageManager): For cleaning up posted parts.
        """
        self.logger = logging.getLogger(__name__)
        self.storage_manager = storage_manager
        self.show_id = storage_manager.show_id

        if not all([config.FACEBOOK_PAGE_ID, config.FACEBOOK_ACCESS_TOKEN]):
            self.logger.warning(
                "Facebook credentials (PAGE_ID, ACCESS_TOKEN) are not fully set. Posting will be skipped.")
            self.is_configured = False
        else:
            self.base_url = f"https://graph-video.facebook.com/v19.0/{config.FACEBOOK_PAGE_ID}/videos"
            self.is_configured = True

    def _generate_caption(self, hosts: List[Dict], guests: List[Dict], part_num: int, total_parts: int) -> str:
        """
        Generates a dynamic caption for the video post.

        Args:
            hosts (List[Dict]): The host characters for the show.
            guests (List[Dict]): The guest characters for the show.
            part_num (int): The current part number.
            total_parts (int): The total number of parts for the show.

        Returns:
            str: The formatted caption string.
        """
        # Ensure consistent order for names in caption
        host_names = sorted([h['name'] for h in hosts])
        guest_names = sorted([g['name'] for g in guests])

        caption = config.POSTING_CAPTION_TEMPLATE.format(
            guest1=guest_names[0],
            guest2=guest_names[1],
            host1=host_names[0],
            host2=host_names[1]
        )

        # Add part number to the caption
        caption += f"\n\nPart {part_num}/{total_parts}"

        return caption

    def post_all_parts(self, video_parts: List[str], hosts: List[Dict], guests: List[Dict]):
        """
        Iterates through video parts and posts them with a delay.

        Args:
            video_parts (List[str]): A list of file paths to the video parts.
            hosts (List[Dict]): The host characters.
            guests (List[Dict]): The guest characters.
        """
        if not self.is_configured:
            self.logger.warning(f"[{self.show_id}] Skipping posting because Facebook is not configured.")
            # Still need to "clean up" the parts as if they were posted
            for part_path in video_parts:
                self.logger.info(f"[{self.show_id}] Simulating post and cleaning up part: {part_path}")
                self.storage_manager.cleanup_posted_part(part_path)
            return

        total_parts = len(video_parts)
        for i, part_path in enumerate(video_parts):
            part_num = i + 1
            self.logger.info(f"[{self.show_id}] Preparing to post Part {part_num}/{total_parts}...")

            caption = self._generate_caption(hosts, guests, part_num, total_parts)

            try:
                self._upload_to_facebook(part_path, caption)
                self.logger.info(f"[{self.show_id}] Successfully posted Part {part_num} to Facebook.")

            except Exception as e:
                self.logger.error(f"[{self.show_id}] FAILED to post Part {part_num}. Error: {e}")
                # Decide on error strategy: continue or stop?
                # For a 24/7 bot, it's better to continue to the next part/show.

            finally:
                # IMPORTANT: Clean up the part file regardless of posting success
                # to prevent disk space from filling up.
                self.storage_manager.cleanup_posted_part(part_path)

                # Wait before posting the next part, unless it's the last one
                if i < total_parts - 1:
                    self.logger.info(f"Waiting {config.POSTING_INTERVAL_SECONDS} seconds before next post...")
                    time.sleep(config.POSTING_INTERVAL_SECONDS)

        self.logger.info(f"[{self.show_id}] All parts have been processed for posting.")

    def _upload_to_facebook(self, video_path: str, caption: str):
        """
        Handles the actual video upload to the Facebook Graph API.
        Facebook requires a two-step resumable upload process.

        Args:
            video_path (str): The path to the video file to upload.
            caption (str): The text to post with the video.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        # Step 1: Initialize the upload session
        self.logger.info(f"[{self.show_id}] Initializing Facebook upload session for {video_path}")
        init_params = {
            'upload_phase': 'start',
            'access_token': config.FACEBOOK_ACCESS_TOKEN,
            'file_size': str(Path(video_path).stat().st_size)
        }
        init_response = requests.post(self.base_url, params=init_params)
        init_response.raise_for_status()
        upload_data = init_response.json()

        upload_session_id = upload_data['upload_session_id']
        video_id = upload_data['video_id']

        self.logger.info(
            f"[{self.show_id}] Upload session created. Session ID: {upload_session_id}, Video ID: {video_id}")

        # Step 2: Upload the video file content
        with open(video_path, 'rb') as video_file:
            transfer_params = {
                'upload_phase': 'transfer',
                'access_token': config.FACEBOOK_ACCESS_TOKEN,
                'upload_session_id': upload_session_id,
                'start_offset': '0'
            }
            files = {'video_file_chunk': video_file}

            self.logger.info(f"[{self.show_id}] Transferring video data...")
            transfer_response = requests.post(self.base_url, params=transfer_params, files=files)
            transfer_response.raise_for_status()

        # Step 3: Finish the upload session and publish the video
        self.logger.info(f"[{self.show_id}] Finishing upload and publishing video...")
        finish_params = {
            'upload_phase': 'finish',
            'access_token': config.FACEBOOK_ACCESS_TOKEN,
            'upload_session_id': upload_session_id,
            'description': caption,
            'published': 'true'  # Set to 'false' to upload as an unpublished video
        }
        finish_response = requests.post(self.base_url, params=finish_params)
        finish_response.raise_for_status()

        if finish_response.json().get('success'):
            self.logger.info(f"[{self.show_id}] Facebook API confirmed successful publishing of video ID: {video_id}")
        else:

            raise RuntimeError(f"Facebook API did not confirm success. Response: {finish_response.json()}")

