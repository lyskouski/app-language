# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
import re
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
    from pydub.silence import detect_nonsilent
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
    AudioSegment = None
    detect_nonsilent = None


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
        recorded_path: str,
        reference_text: str = ""
    ) -> List[Dict[str, Any]]:
        """Compare two audio files and return similarity analysis."""
        if not self.is_available():
            print("Warning: Audio comparison requires numpy, librosa, and pydub")
            return [{"score": 75.0, "feedback": "Audio comparison not available"}]

        print(f"Comparing audio files: {original_path} vs {recorded_path}")

        try:
            words = self._tokenize_words(reference_text)
            if words:
                return self._compare_by_words(original_path, recorded_path, words)
            return self._compare_by_seconds(original_path, recorded_path)
        except Exception as e:
            print(f"Error comparing audio: {e}")
            return [{"score": 0.0, "feedback": f"Error: {str(e)}"}]

    def _compare_by_words(self, original_path: str, recorded_path: str, words: List[str]) -> List[Dict[str, Any]]:
        """Compare two files using word-level timing from reference audio and DTW mapping."""
        features_original, sr_original, hop_length = self._extract_feature_sequence(original_path)
        features_recorded, _, _ = self._extract_feature_sequence(recorded_path)

        # DTW path maps reference frames to recorded frames (forced-alignment style).
        _, path = librosa.sequence.dtw(X=features_original, Y=features_recorded, metric='euclidean')
        path = np.asarray(path)[::-1]

        reference_segments = self._word_boundaries_from_audio(original_path, len(words))
        if not reference_segments:
            return self._compare_by_seconds(original_path, recorded_path)

        summary = []
        for idx, (start_ms, end_ms) in enumerate(reference_segments):
            ref_start = int(librosa.time_to_frames(start_ms / 1000.0, sr=sr_original, hop_length=hop_length))
            ref_end = int(librosa.time_to_frames(end_ms / 1000.0, sr=sr_original, hop_length=hop_length))
            ref_end = max(ref_end, ref_start + 1)

            rec_start, rec_end = self._mapped_recorded_frame_range(path, ref_start, ref_end)
            ref_vector = self._segment_vector(features_original, ref_start, ref_end)
            rec_vector = self._segment_vector(features_recorded, rec_start, rec_end)

            deviation = float(np.linalg.norm(ref_vector - rec_vector))
            score = self._deviation_to_score(deviation)
            word_value = words[idx] if idx < len(words) else f"w{idx + 1}"
            summary.append({
                "word_index": idx + 1,
                "word": word_value,
                "second": idx + 1,
                "deviation": deviation,
                "score": score,
                "feedback": self._feedback_for_score(score)
            })

        return summary

    def _compare_by_seconds(self, original_path: str, recorded_path: str) -> List[Dict[str, Any]]:
        """Fallback comparison split into 1-second chunks."""
        parts_original = self._chunk_audio(original_path)
        parts_recorded = self._chunk_audio(recorded_path)

        summary = []
        try:
            for i, part in enumerate(parts_original):
                deviation = 100.0
                if i < len(parts_recorded):
                    deviation = self._compare_features(part, parts_recorded[i])
                score = self._deviation_to_score(deviation)
                summary.append({
                    "second": i + 1,
                    "deviation": float(deviation),
                    "score": score,
                    "feedback": self._feedback_for_score(score)
                })
            return summary
        finally:
            for part in parts_original + parts_recorded:
                try:
                    if os.path.exists(part):
                        os.remove(part)
                except Exception:
                    pass

    def _tokenize_words(self, reference_text: str) -> List[str]:
        """Extract words from expected sentence for word-level scoring."""
        if not reference_text:
            return []
        return re.findall(r"[\w']+", reference_text, flags=re.UNICODE)

    def _word_boundaries_from_audio(self, audio_path: str, word_count: int) -> List[tuple]:
        """Estimate word boundaries from silence gaps and normalize to expected word count."""
        if word_count <= 0:
            return []

        audio = AudioSegment.from_file(audio_path)
        total_ms = max(int(len(audio)), 1)
        if not detect_nonsilent:
            return self._uniform_segments(total_ms, word_count)

        silence_threshold = audio.dBFS - 20 if audio.dBFS != float('-inf') else -45
        detected = detect_nonsilent(audio, min_silence_len=140, silence_thresh=silence_threshold, seek_step=5)
        segments = [(int(start), int(end)) for start, end in detected if end > start]

        if not segments:
            return self._uniform_segments(total_ms, word_count)

        return self._fit_segments_to_count(segments, word_count, total_ms)

    def _fit_segments_to_count(self, segments: List[tuple], target_count: int, total_ms: int) -> List[tuple]:
        """Merge or split speech segments to match expected word count."""
        normalized = list(segments)

        while len(normalized) > target_count:
            min_idx = 0
            min_gap = float('inf')
            for idx in range(len(normalized) - 1):
                gap = normalized[idx + 1][0] - normalized[idx][1]
                if gap < min_gap:
                    min_gap = gap
                    min_idx = idx
            merged = (normalized[min_idx][0], normalized[min_idx + 1][1])
            normalized[min_idx:min_idx + 2] = [merged]

        while len(normalized) < target_count:
            longest_idx = max(range(len(normalized)), key=lambda i: normalized[i][1] - normalized[i][0])
            start, end = normalized[longest_idx]
            if end - start < 30:
                break
            mid = (start + end) // 2
            normalized[longest_idx:longest_idx + 1] = [(start, mid), (mid, end)]

        if len(normalized) != target_count:
            return self._uniform_segments(total_ms, target_count)
        return normalized

    def _uniform_segments(self, total_ms: int, count: int) -> List[tuple]:
        """Create equal-duration segments as a fallback boundary source."""
        segment_ms = max(total_ms // max(count, 1), 1)
        segments = []
        for idx in range(count):
            start = idx * segment_ms
            end = total_ms if idx == count - 1 else (idx + 1) * segment_ms
            segments.append((start, max(end, start + 1)))
        return segments

    def _extract_feature_sequence(self, file_path: str) -> tuple:
        """Return MFCC feature sequence and timing metadata."""
        y, sr = librosa.load(file_path, sr=16000)
        hop_length = 512
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop_length)
        return mfcc, sr, hop_length

    def _mapped_recorded_frame_range(self, path: Any, ref_start: int, ref_end: int) -> tuple:
        """Map a reference frame span to recorded frame span using DTW path."""
        ref_frames = path[:, 0]
        rec_frames = path[:, 1]
        mask = (ref_frames >= ref_start) & (ref_frames < ref_end)
        if np.any(mask):
            selected = rec_frames[mask]
            rec_start = int(np.min(selected))
            rec_end = int(np.max(selected)) + 1
            return rec_start, rec_end

        nearest_idx = int(np.argmin(np.abs(ref_frames - ref_start)))
        rec_anchor = int(rec_frames[nearest_idx])
        return rec_anchor, rec_anchor + 1

    def _segment_vector(self, features: Any, start_idx: int, end_idx: int) -> Any:
        """Compute mean MFCC vector for a frame interval."""
        max_frames = features.shape[1]
        start = max(0, min(start_idx, max_frames - 1))
        end = max(start + 1, min(end_idx, max_frames))
        return np.mean(features[:, start:end], axis=1)

    def _deviation_to_score(self, deviation: float) -> float:
        """Convert MFCC distance to a 0-100 score (higher is better)."""
        distance = max(float(deviation), 0.0)
        return max(0.0, min(100.0, 100.0 / (1.0 + (distance / 25.0))))

    def _feedback_for_score(self, score: float) -> str:
        """Build a simple quality label for a segment score."""
        if score >= 85.0:
            return "Excellent"
        if score >= 70.0:
            return "Good"
        if score >= 50.0:
            return "Needs improvement"
        return "Try again"

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

    def _extract_features(self, file_path: str) -> Any:
        """Extract MFCC features from audio file."""
        y, sr = librosa.load(file_path, sr=None)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        return np.mean(mfccs.T, axis=0)
