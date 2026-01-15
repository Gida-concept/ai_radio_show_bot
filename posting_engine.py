"""
posting_engine.py
- Handles Facebook Posting.
- Updated for 1-on-1 Interview Format.
"""

import time
import logging
import requests
from pathlib import Path
from typing import List, Dict

import config

class PostingEngine:
    def __init__(self, storage_manager):
        self.logger = logging.getLogger(__name__)
        self.storage_manager = storage_manager
        self.show_id = storage_manager.show_id

        if not all([config.FACEBOOK_PAGE_ID, config.FACEBOOK_ACCESS_TOKEN]):
            self.logger.warning("Facebook credentials missing. Posting skipped.")
            self.is_configured = False
        else:
            self.base_url = f"https://graph-video.facebook.com/v19.0/{config.FACEBOOK_PAGE_ID}/videos"
            self.is_configured = True

    def _generate_caption(self, hosts: List[Dict], guests: List[Dict], part_num: int, total_parts: int) -> str:
        """
        Generates caption for 1 Host vs 1 Guest format.
        """
        host_name = hosts[0]['name']
        guest_name = guests[0]['name']
        topic = guests[0].get('persona', 'Relationship Drama')

        # Use the template from config, or a fallback if template expects 2 guests
        try:
            caption = config.POSTING_CAPTION_TEMPLATE.format(
                host=host_name,
                guest=guest_name
            )
        except KeyError:
            # Fallback if template has {guest2}
            caption = f"💔 The Ex-Files: {host_name} interviews {guest_name} about: {topic}"
        
        caption += f"\n\nPart {part_num}/{total_parts}"
        return caption

    def post_all_parts(self, video_parts: List[str], hosts: List[Dict], guests: List[Dict]):
        if not self.is_configured:
            for part in video_parts:
                self.storage_manager.cleanup_posted_part(part)
            return

        total_parts = len(video_parts)
        for i, part_path in enumerate(video_parts):
            part_num = i + 1
            self.logger.info(f"[{self.show_id}] Posting Part {part_num}/{total_parts}...")
            
            caption = self._generate_caption(hosts, guests, part_num, total_parts)
            
            try:
                self._upload_to_facebook(part_path, caption)
                self.logger.info(f"[{self.show_id}] Posted Part {part_num}.")
            except Exception as e:
                self.logger.error(f"[{self.show_id}] Failed to post Part {part_num}: {e}")
            finally:
                self.storage_manager.cleanup_posted_part(part_path)
                if i < total_parts - 1:
                    time.sleep(config.POSTING_INTERVAL_SECONDS)

    def _upload_to_facebook(self, video_path: str, caption: str):
        # Init
        init = requests.post(self.base_url, params={
            'upload_phase': 'start',
            'access_token': config.FACEBOOK_ACCESS_TOKEN,
            'file_size': str(Path(video_path).stat().st_size)
        }).json()
        
        # Transfer
        with open(video_path, 'rb') as f:
            requests.post(self.base_url, params={
                'upload_phase': 'transfer',
                'access_token': config.FACEBOOK_ACCESS_TOKEN,
                'upload_session_id': init['upload_session_id'],
                'start_offset': '0'
            }, files={'video_file_chunk': f}).raise_for_status()

        # Finish
        res = requests.post(self.base_url, params={
            'upload_phase': 'finish',
            'access_token': config.FACEBOOK_ACCESS_TOKEN,
            'upload_session_id': init['upload_session_id'],
            'description': caption,
            'published': 'true'
        }).json()

        if not res.get('success'):
            raise RuntimeError(f"FB Error: {res}")
