"""
video_engine.py

Uses FFmpeg to assemble the final video.
- Combines background video, background music, and the generated show audio.
- Burns the subtitles onto the video.
- Handles looping/trimming of background media to match the show's duration.
"""

import ffmpeg
import logging
from pathlib import Path
import math
from typing import List  # <--- Added this

import config


class VideoEngine:
    """Assembles the final video using FFmpeg."""

    def __init__(self, storage_manager):
        """
        Initializes the VideoEngine.

        Args:
            storage_manager (StorageManager): An instance to get paths for media.
        """
        self.logger = logging.getLogger(__name__)
        self.storage_manager = storage_manager
        self.show_id = storage_manager.show_id

    def _get_media_duration(self, file_path: str) -> float:
        """
        Gets the duration of a media file in seconds using ffprobe.

        Args:
            file_path (str): Path to the media file.

        Returns:
            float: Duration in seconds.
        """
        try:
            self.logger.debug(f"Probing for duration of: {file_path}")
            probe = ffmpeg.probe(file_path)
            duration = float(probe['format']['duration'])
            self.logger.debug(f"Duration of {Path(file_path).name} is {duration:.2f}s")
            return duration
        except ffmpeg.Error as e:
            self.logger.error(f"Failed to probe {file_path}: {e.stderr.decode('utf8')}")
            raise
        except (KeyError, IndexError):
            self.logger.error(f"Could not find duration in ffprobe output for {file_path}")
            raise ValueError(f"Unable to determine duration for {file_path}")

    def assemble_video(self, master_audio_path: str, subtitle_path: str) -> str:
        """
        Creates the final video by merging all components.

        Args:
            master_audio_path (str): Path to the master show audio (.wav).
            subtitle_path (str): Path to the generated subtitles file (.srt).

        Returns:
            str: The path to the final generated MP4 video file.
        """
        self.logger.info(f"[{self.show_id}] Starting video assembly process.")

        final_video_path = config.VIDEO_DIR / f"final_show_video_{self.show_id}.mp4"
        bg_video_path = self.storage_manager.background_video_path
        bg_music_path = self.storage_manager.background_music_path

        try:
            # 1. Get durations of all media
            show_audio_duration = self._get_media_duration(master_audio_path)
            bg_video_duration = self._get_media_duration(str(bg_video_path))
            bg_music_duration = self._get_media_duration(str(bg_music_path))

            # 2. Prepare background video stream (loop if necessary)
            video_input = ffmpeg.input(str(bg_video_path), stream_loop=-1)
            video_trimmed = video_input.trim(duration=show_audio_duration)

            # 3. Prepare background music stream (loop if necessary)
            music_input = ffmpeg.input(str(bg_music_path), stream_loop=-1)
            music_trimmed = music_input.filter('atrim', duration=show_audio_duration)
            # Lower the volume of the background music to not overpower the voices.
            music_faded = music_trimmed.filter('volume', 0.1)

            # 4. Prepare main voice audio stream
            voice_input = ffmpeg.input(master_audio_path)

            # 5. Mix background music and voice audio
            # amix is a powerful filter for combining audio streams.
            combined_audio = ffmpeg.filter([music_faded, voice_input], 'amix', inputs=2)

            # 6. Burn subtitles onto the video stream
            # The 'force_style' part is for customization, e.g., font size, color.
            # This makes the karaoke-style subtitles appear correctly.
            subtitled_video = video_trimmed.filter(
                'subtitles',
                subtitle_path,
                force_style='Alignment=10,Fontsize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=1,Shadow=0.5'
            )

            # 7. Combine video and mixed audio, and set output options
            # Using 'aac' for audio codec and 'libx264' for video are safe bets for social media.
            # 'shortest' ensures the output terminates when the shortest input (our trimmed video) ends.
            self.logger.info(f"[{self.show_id}] Running FFmpeg command...")
            (
                ffmpeg
                .output(
                    subtitled_video,
                    combined_audio,
                    str(final_video_path),
                    vcodec='libx264',
                    acodec='aac',
                    audio_bitrate='192k',
                    pix_fmt='yuv420p',  # Pixel format for compatibility
                    preset='medium',  # 'fast' or 'veryfast' for speed, 'medium' for better quality/size
                    shortest=None
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            self.logger.info(f"[{self.show_id}] Final video successfully created at: {final_video_path}")
            return str(final_video_path)

        except ffmpeg.Error as e:
            self.logger.critical(f"[{self.show_id}] FFmpeg error during video assembly.")
            self.logger.error(f"FFmpeg stdout: {e.stdout.decode('utf8')}")
            self.logger.error(f"FFmpeg stderr: {e.stderr.decode('utf8')}")
            raise RuntimeError("FFmpeg failed to assemble the video.") from e

    def split_video_into_parts(self, final_video_path: str) -> List[str]:
        """
        Splits the final video into 2.5-minute parts.

        Args:
            final_video_path (str): The path to the complete show video.

        Returns:
            A list of file paths for the generated parts.
        """
        self.logger.info(f"[{self.show_id}] Splitting video into {config.PART_DURATION_SECONDS}s parts.")

        video_duration = self._get_media_duration(final_video_path)
        num_parts = math.ceil(video_duration / config.PART_DURATION_SECONDS)
        part_paths = []

        self.logger.info(f"[{self.show_id}] Video duration {video_duration:.2f}s will be split into {num_parts} parts.")

        try:
            for i in range(num_parts):
                start_time = i * config.PART_DURATION_SECONDS
                part_path = self.storage_manager.show_parts_dir / f"part_{i + 1}.mp4"

                # Use ffmpeg to seek to the start time and copy the stream for a specific duration.
                # '-c copy' is extremely fast as it avoids re-encoding.
                (
                    ffmpeg
                    .input(final_video_path, ss=start_time)
                    .output(str(part_path), c='copy', t=config.PART_DURATION_SECONDS)
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
                part_paths.append(str(part_path))
                self.logger.info(f"[{self.show_id}] Created part {i + 1}: {part_path}")

            self.logger.info(f"[{self.show_id}] Successfully split video into {len(part_paths)} parts.")
            return part_paths

        except ffmpeg.Error as e:
            self.logger.critical(f"[{self.show_id}] FFmpeg error during video splitting.")
            self.logger.error(f"FFmpeg stderr: {e.stderr.decode('utf8')}")

            raise RuntimeError("FFmpeg failed to split the video.") from e
