# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
import re
from math import ceil
from typing import Any, Dict, List

from domain.services.audio_comparator import IAudioComparator


class MobileAudioComparatorBase(IAudioComparator):
    """Shared fallback logic for mobile metadata-based audio comparators."""

    def compare_audio(
        self,
        original_path: str,
        recorded_path: str,
        reference_text: str = ""
    ) -> List[Dict[str, Any]]:
        if not self.is_available():
            return [{"score": 0.0, "feedback": "Audio comparison not available"}]

        original_meta = self._read_metadata(original_path)
        recorded_meta = self._read_metadata(recorded_path)

        duration_score = self._similarity_score(
            original_meta.get('duration_ms', 0.0),
            recorded_meta.get('duration_ms', 0.0)
        )
        size_score = self._similarity_score(
            original_meta.get('size_bytes', 0.0),
            recorded_meta.get('size_bytes', 0.0)
        )

        overall_score = self._compute_overall_score(original_meta, recorded_meta, duration_score, size_score)
        overall_score = max(0.0, min(100.0, overall_score))

        words = self._tokenize_words(reference_text)
        if words:
            return self._build_word_results(words, overall_score, duration_score)

        return self._build_second_results(
            duration_ms=max(original_meta.get('duration_ms', 0.0), 1000.0),
            overall_score=overall_score,
            duration_score=duration_score,
        )

    def _read_metadata(self, file_path: str) -> Dict[str, float]:
        metadata = {
            'duration_ms': 0.0,
            'size_bytes': 0.0,
        }

        try:
            if file_path and os.path.exists(file_path):
                metadata['size_bytes'] = float(os.path.getsize(file_path))
        except Exception:
            pass

        if not file_path or not os.path.exists(file_path):
            return metadata

        try:
            platform_metadata = self._read_platform_metadata(file_path)
            if platform_metadata:
                metadata.update(platform_metadata)
        except Exception:
            pass

        return metadata

    def _read_platform_metadata(self, file_path: str) -> Dict[str, float]:
        raise NotImplementedError()

    def _compute_overall_score(
        self,
        original_meta: Dict[str, float],
        recorded_meta: Dict[str, float],
        duration_score: float,
        size_score: float,
    ) -> float:
        return (duration_score * 0.75) + (size_score * 0.25)

    def _similarity_score(self, value_a: float, value_b: float) -> float:
        a = max(float(value_a), 0.0)
        b = max(float(value_b), 0.0)
        max_value = max(a, b, 1.0)
        diff = abs(a - b)
        return max(0.0, min(100.0, 100.0 * (1.0 - (diff / max_value))))

    def _tokenize_words(self, reference_text: str) -> List[str]:
        if not reference_text:
            return []
        return re.findall(r"[\w']+", reference_text, flags=re.UNICODE)

    def _build_word_results(self, words: List[str], overall_score: float, duration_score: float) -> List[Dict[str, Any]]:
        result = []
        for idx, word in enumerate(words):
            spread = min(8.0, idx * 1.5)
            score = max(0.0, min(100.0, overall_score - spread + ((duration_score - 50.0) * 0.05)))
            result.append({
                'word_index': idx + 1,
                'word': word,
                'second': idx + 1,
                'deviation': float(100.0 - score),
                'score': float(score),
                'feedback': self._feedback_for_score(score),
            })
        return result

    def _build_second_results(self, duration_ms: float, overall_score: float, duration_score: float) -> List[Dict[str, Any]]:
        seconds = max(1, min(10, int(ceil(duration_ms / 1000.0))))
        result = []
        for idx in range(seconds):
            wave = (idx % 3) * 1.8
            score = max(0.0, min(100.0, overall_score - wave + ((duration_score - 50.0) * 0.04)))
            result.append({
                'second': idx + 1,
                'deviation': float(100.0 - score),
                'score': float(score),
                'feedback': self._feedback_for_score(score),
            })
        return result

    def _feedback_for_score(self, score: float) -> str:
        if score >= 85.0:
            return 'Excellent'
        if score >= 70.0:
            return 'Good'
        if score >= 50.0:
            return 'Needs improvement'
        return 'Try again'
