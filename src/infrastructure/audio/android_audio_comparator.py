# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from typing import Dict

from infrastructure.audio.mobile_audio_comparator_base import MobileAudioComparatorBase

try:
    from jnius import autoclass
    HAS_JNIUS = True
except ImportError:
    HAS_JNIUS = False
    autoclass = None


class AndroidAudioComparator(MobileAudioComparatorBase):
    """
    Lightweight Android comparator that uses MediaMetadataRetriever.
    This provides an on-device fallback when librosa is unavailable.
    """

    def __init__(self):
        self._retriever_class = None
        if HAS_JNIUS:
            try:
                self._retriever_class = autoclass('android.media.MediaMetadataRetriever')
            except Exception:
                self._retriever_class = None

    def is_available(self) -> bool:
        return self._retriever_class is not None

    def _compute_overall_score(
        self,
        original_meta: Dict[str, float],
        recorded_meta: Dict[str, float],
        duration_score: float,
        size_score: float,
    ) -> float:
        bitrate_original = original_meta.get('bitrate', 0.0)
        bitrate_recorded = recorded_meta.get('bitrate', 0.0)
        if bitrate_original > 0.0 and bitrate_recorded > 0.0:
            bitrate_score = self._similarity_score(bitrate_original, bitrate_recorded)
            return (duration_score * 0.65) + (size_score * 0.2) + (bitrate_score * 0.15)
        return super()._compute_overall_score(original_meta, recorded_meta, duration_score, size_score)

    def _read_platform_metadata(self, file_path: str) -> Dict[str, float]:
        metadata = {
            'duration_ms': 0.0,
            'bitrate': 0.0,
        }

        retriever = None
        try:
            retriever = self._retriever_class()
            retriever.setDataSource(file_path)
            duration_value = retriever.extractMetadata(9)  # METADATA_KEY_DURATION
            bitrate_value = retriever.extractMetadata(20)  # METADATA_KEY_BITRATE
            metadata['duration_ms'] = float(duration_value) if duration_value else 0.0
            metadata['bitrate'] = float(bitrate_value) if bitrate_value else 0.0
        except Exception:
            pass
        finally:
            if retriever is not None:
                try:
                    retriever.release()
                except Exception:
                    pass

        return metadata
