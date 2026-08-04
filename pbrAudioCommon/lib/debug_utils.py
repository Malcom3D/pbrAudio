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

import sys
import os
from typing import Any
from dataclasses import dataclass

@dataclass
class DebugConfig:
    enabled: bool = False
    prefix: str = ""
    output: Any = sys.stdout

# Global config instance
config = DebugConfig()

def debug_print(*args, **kwargs):
    """Print debug messages"""
    if config.enabled:
        print(f"[{config.prefix}]", *args, file=config.output, **kwargs)


# Control functions
def set_debug(enabled):
    """Enable/disable debug output globally"""
    config.enabled = enabled

def set_debug_output(output):
    """Set debug file output"""
    config.output = output

def set_debug_prefix(prefix):
    """Change the debug message prefix"""
    config.prefix = prefix
