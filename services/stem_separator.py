# Stem-Separator: This portion of the project is used to seperate sounds into sections. say you are given a song, it seperates it into the vocals, guitar, drums, and other instraments. 
# programer: Ginnie Steck

import logging
import demucs.separate
from pathlib import Path

logger = logging.getLogger(__name__)

class StemSeparator:
    def __init__(self, output_dir="separated/"):
        self.output_dir = output_dir

    def separate(self, audio_path: str, two_stems: str = None):
        """Separate audio into stems."""
        args = ["-n", "htdemucs_6s", "--out", self.output_dir]
        if two_stems:
            args.append(f"--two-stems={two_stems}")
        args.append(str(audio_path))
        logger.info(f"Separating stems for: {audio_path}")
        demucs.separate.main(args)

    def get_stems(self, filename: str):
        """Return paths to separated files."""
        name = Path(filename).stem
        base = Path(self.output_dir) / "htdemucs" / name
        return {
             "vocals": base / "vocals.wav",
            "drums": base / "drums.wav",
            "bass": base / "bass.wav",
            "guitar": base / "guitar.wav",
            "piano": base / "piano.wav",
            "other": base / "other.wav",
        }