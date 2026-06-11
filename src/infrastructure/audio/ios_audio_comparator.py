# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from typing import Any, Dict

from infrastructure.audio.mobile_audio_comparator_base import MobileAudioComparatorBase

try:
    from pyobjus import autoclass, objc_str
    HAS_PYOBJUS = True
except ImportError:
    HAS_PYOBJUS = False
    autoclass = None
    objc_str = None


class IosAudioComparator(MobileAudioComparatorBase):
    """
    Lightweight iOS comparator using AVAudioPlayer metadata.
    This provides an on-device fallback when librosa is unavailable.
    """

    def __init__(self):
        self._url_class = None
        self._player_class = None
        if HAS_PYOBJUS:
            try:
                self._url_class = autoclass('NSURL')
                self._player_class = autoclass('AVAudioPlayer')
            except Exception:
                self._url_class = None
                self._player_class = None

    def is_available(self) -> bool:
        return self._url_class is not None and self._player_class is not None

    def _read_platform_metadata(self, file_path: str) -> Dict[str, float]:
        metadata = {
            'duration_ms': 0.0,
        }

        try:
            file_url = self._url_class.fileURLWithPath_(objc_str(file_path))
            player = self._player_class.alloc().initWithContentsOfURL_error_(file_url, None)
            if player:
                try:
                    player.prepareToPlay()
                except Exception:
                    pass
                metadata['duration_ms'] = float(self._read_duration_seconds(player) * 1000.0)
        except Exception:
            pass

        return metadata

    def _read_duration_seconds(self, player: Any) -> float:
        try:
            value = player.duration()
            return max(float(value), 0.0)
        except Exception:
            pass

        try:
            value = getattr(player, 'duration', 0.0)
            return max(float(value), 0.0)
        except Exception:
            return 0.0
