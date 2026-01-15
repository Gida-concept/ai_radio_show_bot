"""
subtitle_engine.py

Handles the generation of subtitles from an audio file using Groq's Whisper API.
- Transcribes the master audio track.
- Requests word-level timestamps from the API.
- Formats the transcription into a karaoke-style SRT file.
"""

import logging
from pathlib import Path
from groq import Groq

import config


class SubtitleEngine:
    """Uses Groq Whisper API to generate word-level subtitles."""

    def __init__(self):
        """Initializes the SubtitleEngine with the Groq client."""
        self.logger = logging.getLogger(__name__)
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in configuration.")

        try:
            self.client = Groq(api_key=config.GROQ_API_KEY)
            self.logger.info("Groq client initialized successfully for Whisper.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize Groq client: {e}")
            raise

    def _format_timestamp(self, seconds: float) -> str:
        """Converts seconds into SRT timestamp format (HH:MM:SS,ms)."""
        assert seconds >= 0, "non-negative timestamp expected"
        milliseconds = round(seconds * 1000.0)

        hours = milliseconds // 3_600_000
        milliseconds %= 3_600_000
        minutes = milliseconds // 60_000
        milliseconds %= 60_000
        seconds = milliseconds // 1_000
        milliseconds %= 1_000

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def generate_subtitles(self, master_audio_path: str, show_id: str) -> str:
        """
        Transcribes an audio file and creates a karaoke-style SRT subtitle file.

        Args:
            master_audio_path (str): The path to the master audio file (.wav).
            show_id (str): The unique identifier for the current show.

        Returns:
            The file path to the generated SRT subtitle file.

        Raises:
            Exception: If the Groq API call fails.
        """
        self.logger.info(f"[{show_id}] Starting subtitle generation for: {master_audio_path}")

        output_srt_path = config.SUBTITLES_DIR / f"subtitles_{show_id}.srt"

        try:
            with open(master_audio_path, "rb") as audio_file:
                self.logger.info(f"[{show_id}] Uploading audio to Groq Whisper API...")

                transcription = self.client.audio.transcriptions.create(
                    file=(Path(master_audio_path).name, audio_file.read()),
                    model=config.GROQ_WHISPER_MODEL,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]# Must be verbose_json for word timestamps
                    # language="en" # Optional: specify language
                )
                self.logger.info(f"[{show_id}] Successfully received transcription from Groq.")

            # Process the response to create an SRT file
            with open(output_srt_path, "w", encoding="utf-8") as srt_file:
                srt_counter = 1
                # 'words' is the key for word-level timestamps in the verbose_json response
                if not hasattr(transcription, 'words') or not transcription.words:
                    self.logger.warning(
                        f"[{show_id}] Groq transcription did not return word-level timestamps. Falling back to segment-level.")
                    # Fallback for older API versions or unexpected responses
                    for i, segment in enumerate(transcription.segments):
                        start_time = self._format_timestamp(segment['start'])
                        end_time = self._format_timestamp(segment['end'])
                        text = segment['text'].strip()
                        srt_file.write(f"{i + 1}\n")
                        srt_file.write(f"{start_time} --> {end_time}\n")
                        srt_file.write(f"{text}\n\n")
                    srt_counter = len(transcription.segments) + 1
                else:
                    # Ideal case: Generate karaoke-style subtitles
                    for word in transcription.words:
                        start_time = self._format_timestamp(word['start'])
                        end_time = self._format_timestamp(word['end'])
                        text = word['word'].strip()

                        srt_file.write(f"{srt_counter}\n")
                        srt_file.write(f"{start_time} --> {end_time}\n")
                        srt_file.write(f"{text}\n\n")
                        srt_counter += 1

            self.logger.info(f"[{show_id}] Karaoke-style SRT file created at: {output_srt_path}")
            return str(output_srt_path)

        except Exception as e:
            self.logger.critical(f"[{show_id}] An error occurred with the Groq Whisper API: {e}")

            raise  # Propagate the exception to halt the current show generation
