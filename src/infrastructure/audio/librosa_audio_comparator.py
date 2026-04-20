# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
from typing import List, Dict, Any
from domain.services.audio_comparator import IAudioComparator

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    librosa = None

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
    AudioSegment = None


class LibrosaAudioComparator(IAudioComparator):
    """
    Audio comparator implementation using librosa for feature extraction.
    Infrastructure implementation of the domain interface.
    """

    def is_available(self) -> bool:
        """Check if all required dependencies are available."""
        return HAS_NUMPY and HAS_LIBROSA and HAS_PYDUB

    def compare_audio(
        self,
        original_path: str,
        recorded_path: str
    ) -> List[Dict[str, Any]]:
        """Compare two audio files and return similarity analysis."""
        if not self.is_available():
            print("Warning: Audio comparison requires numpy, librosa, and pydub")
            return [{"score": 75.0, "feedback": "Audio comparison not available"}]

        print(f"Comparing audio files: {original_path} vs {recorded_path}")

        try:
            parts_original = self._chunk_audio(original_path)
            parts_recorded = self._chunk_audio(recorded_path)

            summary = []
            for i, part in enumerate(parts_original):
                deviation = 100.0
                if i < len(parts_recorded):
                    deviation = self._compare_features(part, parts_recorded[i])
                summary.append({
                    "second": i,
                    "deviation": float(deviation)
                })

            # Cleanup chunk files
            for part in parts_original + parts_recorded:
                try:
                    if os.path.exists(part):
                        os.remove(part)
                except Exception:
                    pass

            return summary
        except Exception as e:
            print(f"Error comparing audio: {e}")
            return [{"score": 0.0, "feedback": f"Error: {str(e)}"}]

    def _chunk_audio(self, audio_path: str) -> List[str]:
        """Split audio into 1-second chunks."""
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        chunk_length_ms = 1000
        chunks = []
        base, _ = os.path.splitext(audio_path)

        for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
            chunk = audio[start:start + chunk_length_ms]
            chunk_path = f"{base}_chunk{i+1}.wav"
            chunk.export(chunk_path, format="wav")
            chunks.append(chunk_path)

        return chunks

    def _compare_features(self, audio_original: str, audio_recorded: str) -> float:
        """Compare features between two audio chunks."""
        features_original = self._extract_features(audio_original)
        features_recorded = self._extract_features(audio_recorded)
        return float(np.linalg.norm(features_original - features_recorded))

    def _extract_features(self, file_path: str) -> np.ndarray:
        """Extract MFCC features from audio file."""
        y, sr = librosa.load(file_path, sr=None)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        return np.mean(mfccs.T, axis=0)
