# Copyright (C) 2025 Malcom3D <malcom3d.gpl@gmail.com>
#
# This file is part of pbrAudio.
#
# pbrAudio is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pbrAudio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pbrAudio.  If not, see <https://www.gnu.org/licenses/>.
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, field
from typing import List, Tuple

from ..core.entity_manager import EntityManager
from ..lib.functions import _generate_band_frequencies

@dataclass
class FrequencyBands:
    entity_manager: EntityManager
    freq_bands: List[Tuple[float, float]] = field(default_factory=list)

    def __post_init__(self) -> List[Tuple]:
        """Lazy property that computes frequencies when first accessed"""
        config = self.entity_manager.get('config')
        higher_frequency = config.system.sample_rate / 2
        lowest_frequency = config.system.lowest_frequency
        bands_per_octave = config.system.bands_per_octave
        frequencies = _generate_band_frequencies(lowest_frequency, higher_frequency, bands_per_octave)
        for index in range(len(frequencies)-1):
            low = frequencies[index]
            high = frequencies[index+1]
            self.freq_bands.append((low,high))
        self.freq_bands.append((frequencies[-1],higher_frequency))

    def get_bands(self):
        return self.freq_bands
