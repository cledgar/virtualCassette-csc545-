# Stem-Separator: This portion of the project is used to seperate sounds into sections. say you are given a song, it seperates it into the vocals, guitar, drums, and other instraments. 
# programer: Ginnie Steck

import logging
import subprocess
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class StemSeparator:
    def __init__(self, output_dir="separated/"):
        self.output_dir = output_dir

    def separate(self, audio_path: str, two_stems: Optional[str] = None):
        """Separate audio into stems using demucs CLI."""
        try:
            model = "mdx_extra_q"  # Use mdx_extra_q which works better
            args = ["python", "-m", "demucs.separate", "-n", model, "--out", self.output_dir]
            if two_stems:
                args.append(f"--two-stems={two_stems}")
            args.append(str(audio_path))
            logger.info(f"Separating stems for: {audio_path}")
            result = subprocess.run(args, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"Demucs separation failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Stem separation timed out after 5 minutes")
        except Exception as e:
            logger.error(f"Stem separation failed: {e}")
            raise RuntimeError(f"Stem separation failed: {e}")

    def get_stems(self, filename: str):
        """Return paths to separated files."""
        name = Path(filename).stem
        
        # Try both possible folder names (mdx_extra_q is the model we use now)
        base_mdx = Path(self.output_dir) / "mdx_extra_q" / name
        base_6s = Path(self.output_dir) / "htdemucs_6s" / name
        base_default = Path(self.output_dir) / "htdemucs" / name
        
        # Use whichever exists
        if base_mdx.exists():
            base = base_mdx
        elif base_6s.exists():
            base = base_6s
        elif base_default.exists():
            base = base_default
        else:
            # Default to mdx_extra_q
            base = base_mdx
        
        # mdx_extra_q produces vocals, drums, bass, other
        stems = {
            "vocals": base / "vocals.wav",
            "drums": base / "drums.wav",
            "bass": base / "bass.wav",
            "other": base / "other.wav",
        }
        
        # Return only stems that exist
        return {k: v for k, v in stems.items() if v.exists()}