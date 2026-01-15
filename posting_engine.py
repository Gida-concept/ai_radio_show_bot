"""
posting_engine.py
- Handles Facebook Posting.
- Updated for 1-on-1 Interview Format.
- Improved error handling and retry logic.
"""

import time
import logging
import requests
from pathlib import Path
from typing import List, Dict
from requests.exceptions import RequestException

import config

class PostingEngine:
    def __init__(self, storage_manager):
        self.logger = logging.getLogger(__name__)
        self.storage_manager = storage_manager
        self.show_id = storage_manager.show_id

        if not all([config.FACEBOOK_PAGE_ID, config.FACEBOOK_ACCESS_TOKEN]):
            self.logger.warning("Facebook credentials missing. Posting will be skipped.")
            self.is_configured = False
        else:
            # Updated to v22.0 (current stable version as of Jan 2026)
            self.base_url = f"https://graph-video.facebook.com/v22.0/{config.FACEBOOK_PAGE_ID}/videos"
            self.is_configured = True
            self.logger.info(f"Facebook posting configured for Page ID: {config.FACEBOOK_PAGE_ID}")

    def _generate_caption(self, hosts: List[Dict], guests: List[Dict], part_num: int, total_parts: int) -> str:
        """
        Generates caption for 1 Host vs 1 Guest format.
        Includes part indicator if video is split.
        """
        host_name = hosts[0]['name']
        guest_name = guests[0]['name']
        topic = guests[0].get('persona', 'Relationship Drama')

        # Use the template from config, with fallback
        try:
            caption = config.POSTING_CAPTION_TEMPLATE.format(
                host=host_name,
                guest=guest_name
            )
        except KeyError:
            # Fallback if template has unexpected placeholders
            caption = f"💔 The Ex-Files: {host_name} interviews {guest_name} about: {topic}"
        
        # Add part indicator for multi-part videos
        if total_parts > 1:
            if part_num == 1:
                caption += f"\n\n🎬 PART {part_num}/{total_parts} | More coming in 10 minutes..."
            elif part_num == total_parts:
                caption += f"\n\n🎬 FINAL PART ({part_num}/{total_parts}) | Did you watch from the start?"
            else:
                caption += f"\n\n🎬 PART {part_num}/{total_parts}"
        
        return caption

    def post_all_parts(self, video_parts: List[str], hosts: List[Dict], guests: List[Dict]):
        """
        Posts all video parts to Facebook with configured delays between parts.
        """
        if not self.is_configured:
            self.logger.warning(f"[{self.show_id}] Posting skipped (not configured). Cleaning up parts.")
            for part in video_parts:
                self.storage_manager.cleanup_posted_part(part)
            return

        total_parts = len(video_parts)
        self.logger.info(f"[{self.show_id}] Starting to post {total_parts} part(s) to Facebook.")
        
        for i, part_path in enumerate(video_parts):
            part_num = i + 1
            self.logger.info(f"[{self.show_id}] Posting Part {part_num}/{total_parts}...")
            
            caption = self._generate_caption(hosts, guests, part_num, total_parts)
            
            try:
                self._upload_to_facebook(part_path, caption)
                self.logger.info(f"[{self.show_id}] ✅ Successfully posted Part {part_num}.")
            except Exception as e:
                self.logger.error(f"[{self.show_id}] ❌ Failed to post Part {part_num}: {e}", exc_info=True)
            finally:
                # Always cleanup the part file after attempting to post
                self.storage_manager.cleanup_posted_part(part_path)
                
                # Wait between parts (but not after the last one)
                if i < total_parts - 1:
                    wait_time = config.POSTING_INTERVAL_SECONDS
                    self.logger.info(f"[{self.show_id}] Waiting {wait_time} seconds before posting next part...")
                    time.sleep(wait_time)
        
        self.logger.info(f"[{self.show_id}] All parts posted successfully.")

    def _upload_to_facebook(self, video_path: str, caption: str, max_retries: int = 3):
        """
        Uploads a video to Facebook using the resumable upload API.
        Implements retry logic for network failures.
        
        Args:
            video_path: Path to the video file
            caption: Video description/caption
            max_retries: Number of retry attempts for failed uploads
        """
        file_size = Path(video_path).stat().st_size
        
        for attempt in range(max_retries):
            try:
                # PHASE 1: Initialize Upload Session
                self.logger.debug(f"Initializing upload session (attempt {attempt + 1}/{max_retries})...")
                init_response = requests.post(
                    self.base_url,
                    params={
                        'upload_phase': 'start',
                        'access_token': config.FACEBOOK_ACCESS_TOKEN,
                        'file_size': str(file_size)
                    },
                    timeout=30
                ).json()
                
                # Check for errors in init response
                if 'error' in init_response:
                    raise RuntimeError(f"FB Init Error: {init_response['error']}")
                
                if 'upload_session_id' not in init_response:
                    raise RuntimeError(f"No upload_session_id in response: {init_response}")
                
                upload_session_id = init_response['upload_session_id']
                self.logger.debug(f"Upload session initialized: {upload_session_id}")
                
                # PHASE 2: Transfer Video Data
                self.logger.debug("Transferring video data...")
                with open(video_path, 'rb') as video_file:
                    transfer_response = requests.post(
                        self.base_url,
                        params={
                            'upload_phase': 'transfer',
                            'access_token': config.FACEBOOK_ACCESS_TOKEN,
                            'upload_session_id': upload_session_id,
                            'start_offset': '0'
                        },
                        files={'video_file_chunk': video_file},
                        timeout=300  # 5 minutes for large files
                    )
                    transfer_response.raise_for_status()
                
                # Check transfer response
                transfer_data = transfer_response.json()
                if 'error' in transfer_data:
                    raise RuntimeError(f"FB Transfer Error: {transfer_data['error']}")
                
                self.logger.debug("Video data transferred successfully.")
                
                # PHASE 3: Finish Upload and Publish
                self.logger.debug("Finalizing upload and publishing...")
                finish_response = requests.post(
                    self.base_url,
                    params={
                        'upload_phase': 'finish',
                        'access_token': config.FACEBOOK_ACCESS_TOKEN,
                        'upload_session_id': upload_session_id,
                        'description': caption,
                        'published': 'true'  # Publish immediately
                    },
                    timeout=60
                ).json()
                
                # Check finish response
                if 'error' in finish_response:
                    raise RuntimeError(f"FB Finish Error: {finish_response['error']}")
                
                if not finish_response.get('success'):
                    raise RuntimeError(f"Upload failed: {finish_response}")
                
                video_id = finish_response.get('id', 'unknown')
                self.logger.info(f"Video uploaded successfully. Facebook Video ID: {video_id}")
                
                return  # Success - exit retry loop
                
            except (RequestException, RuntimeError) as e:
                if attempt < max_retries - 1:
                    retry_delay = 30 * (attempt + 1)  # Exponential backoff: 30s, 60s, 90s
                    self.logger.warning(
                        f"Upload failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                else:
                    # Final attempt failed
                    self.logger.error(f"Upload failed after {max_retries} attempts: {e}")
                    raise
