"""
video_engine.py
- PRECISE SPLITTING (Re-encoding for accuracy).
- Handles looping backgrounds perfectly.
"""

import ffmpeg
import logging
from pathlib import Path
import math
from typing import List

import config

class VideoEngine:
    """Assembles the final video using FFmpeg."""

    def __init__(self, storage_manager):
        self.logger = logging.getLogger(__name__)
        self.storage_manager = storage_manager
        self.show_id = storage_manager.show_id

    def _get_media_duration(self, file_path: str) -> float:
        try:
            probe = ffmpeg.probe(file_path)
            return float(probe['format']['duration'])
        except Exception as e:
            self.logger.error(f"Probe failed: {e}")
            return 0.0

    def assemble_video(self, master_audio_path: str, subtitle_path: str) -> str:
        self.logger.info(f"[{self.show_id}] Assembling video...")
        
        final_video_path = config.VIDEO_DIR / f"final_show_video_{self.show_id}.mp4"
        bg_video_path = self.storage_manager.background_video_path
        bg_music_path = self.storage_manager.background_music_path

        try:
            audio_duration = self._get_media_duration(master_audio_path)
            
            # Inputs
            video_input = ffmpeg.input(str(bg_video_path), stream_loop=-1)
            music_input = ffmpeg.input(str(bg_music_path), stream_loop=-1)
            voice_input = ffmpeg.input(master_audio_path)

            # Trim to audio length
            video_trimmed = video_input.trim(duration=audio_duration)
            music_trimmed = music_input.filter('atrim', duration=audio_duration).filter('volume', 0.1)
            
            # Mix Audio
            final_audio = ffmpeg.filter([music_trimmed, voice_input], 'amix', inputs=2)

            # Burn Subtitles
            subtitled_video = video_trimmed.filter(
                'subtitles',
                subtitle_path,
                force_style='Alignment=10,Fontsize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=1,Shadow=0.5'
            )

            (
                ffmpeg
                .output(
                    subtitled_video,
                    final_audio,
                    str(final_video_path),
                    vcodec='libx264',
                    acodec='aac',
                    audio_bitrate='192k',
                    preset='fast', 
                    shortest=None
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            self.logger.info(f"[{self.show_id}] Final video created: {final_video_path}")
            return str(final_video_path)

        except ffmpeg.Error as e:
            self.logger.critical(f"FFmpeg Assembly Error: {e.stderr.decode('utf8')}")
            raise

    def split_video_into_parts(self, final_video_path: str) -> List[str]:
        """
        Splits video into precise parts using re-encoding.
        """
        self.logger.info(f"[{self.show_id}] Splitting video...")
        
        video_duration = self._get_media_duration(final_video_path)
        part_duration = config.PART_DURATION_SECONDS
        
        # If video is short (< 4 mins), keep as one part
        if video_duration < 240:
            self.logger.info(f"Video is short ({video_duration}s). Keeping as 1 part.")
            part_path = self.storage_manager.show_parts_dir / "part_1.mp4"
            try:
                (
                    ffmpeg
                    .input(final_video_path)
                    .output(str(part_path), c='copy')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
                return [str(part_path)]
            except ffmpeg.Error as e:
                self.logger.error(f"Split Copy Error: {e.stderr.decode('utf8')}")
                raise

        # Calculate Parts
        num_parts = math.ceil(video_duration / part_duration)
        part_paths = []

        try:
            for i in range(num_parts):
                start_time = i * part_duration
                
                # Skip tiny leftover parts (< 10s)
                if (video_duration - start_time) < 10: 
                    continue

                part_path = self.storage_manager.show_parts_dir / f"part_{i+1}.mp4"
                
                self.logger.info(f"Processing Part {i+1}: Start={start_time}s")

                # RE-ENCODE (Fixes the glitch)
                # Removed c='copy', added vcodec='libx264'
                (
                    ffmpeg
                    .input(final_video_path, ss=start_time)
                    .output(str(part_path), t=part_duration, vcodec='libx264', acodec='aac')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
                part_paths.append(str(part_path))
            
            return part_paths

        except ffmpeg.Error as e:
            self.logger.critical(f"FFmpeg Split Error: {e.stderr.decode('utf8')}")
            raise
