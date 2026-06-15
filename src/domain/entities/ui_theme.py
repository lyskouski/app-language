# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class UITheme:
    """Immutable UI theme definition consumed by the presentation layer."""

    md3_primary: List[float]
    md3_secondary: List[float]
    md3_surface: List[float]
    md3_surface_container: List[float]
    md3_surface_variant: List[float]
    md3_outline: List[float]
    md3_on_primary: List[float]
    md3_on_secondary: List[float]
    md3_on_surface: List[float]
    md3_on_surface_variant: List[float]
    md3_button_height: float
    md3_textinput_height: float
