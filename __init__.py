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
# SPDX-FileCopyrightText: 2024 Blender Foundation
#
# SPDX-License-Identifier: GPL-2.0-or-later

import platform
import os
import sys
import subprocess
import shutil
import pathlib
import hashlib
import base64

import bpy
import addon_utils

# Check firts if Blender and OS versions are compatible
if bpy.app.version < (4, 5, 0):
    raise Exception("\n\nUnsupported Blender version. 4.5 or higher is required by pbrAudio.")

if not platform.system() in {"Linux"}:
    raise Exception("\n\nUnsupported OS version. pbrAudio currently only supports Linux.")

bl_info = {
    "name": "pbrAudio Render Engine",
    "author": "Malcom3D",
    "version": (0, 2, 0),
    "blender": (4, 5, 0),
    "category": "Render",
    "location": "Render Engine > pbrAudio",
    "description": "Physically Based Audio Rendering Engine for Blender",
    "warning": "alpha",
    "doc_url": "https://pbraudio.org",
}

version_string = f'{bl_info["version"][0]}.{bl_info["version"][1]}.{bl_info["version"][2]}'
if 'warning' in bl_info:
    version_string = version_string + f'-{bl_info["warning"]}'

from . import engine gui handlers nodes nodetrees operators sockets

def register():
    print("Register", __package__)
    engine.register()
    nodetrees.register()
    sockets.register()
    nodes.register()
    operators.register()
    handlers.register()
    gui.register()


def unregister():
    print("UnRegister", __package__)
    engine.unregister()
    nodetrees.unregister()
    sockets.unregister()
    nodes.unregister()
    operators.unregister()
    handlers.unregister()
    gui.unregister()

if __name__ == "__main__":
    register()
