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

import os
import re
import gzip
import json
import blosc2
import tarfile
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional, Union

@dataclass
class ScoreEvent:
    """Represents the score for a single collision"""
    coll_obj: int
    start_sample: int
    stop_sample: int
    type: np.ndarray # shape(total_samples,1, dtype=np.int32)
    vertex_ids: Union[blosc2.ndarray.NDArray, np.ndarray]  # shape(total_samples,n_vertices)
    contact_area: np.ndarray = None # shape(total_samples,1)
    force: np.ndarray = None # shape(total_samples,1) Excitation force magnitude
    coupling_data: np.ndarray = None # shape(total_samples,1) Array of [other_obj_idx, coupling_strength] pairs

    def get_event_at_sample(self, sample_idx: int):
        """Get all events at a specific sample index."""
        return self.type[sample_idx][0], np.unique(np.nonzero(self.vertex_ids[sample_idx])).tolist(), self.force[sample_idx], self.contact_area[sample_idx], self.coll_obj, self.coupling_data[sample_idx]

    def save(self, output_path: str, obj_idx: int, idx: int):

        score_event = {
            'coll_obj': self.coll_obj,
            'start_sample': self.start_sample,
            'stop_sample': self.stop_sample
        }
    
        filenames = []
        # Save score_event to file
        json_file = f"{obj_idx}_{self.coll_obj}_{idx}.json"
        with open(f"{output_path}/{json_file}", 'w') as f:
            json.dump(score_event, f, indent=2)

        filenames.append(json_file)

        filename = f"{obj_idx}_{self.coll_obj}_{idx}_vertex_ids.b2"
        blosc2.save(self.vertex_ids, f"{output_path}/{filename}", mode="w")
        filenames.append(filename)

        filename = f"{obj_idx}_{self.coll_obj}_{idx}_type.bl2"
        blosc2.save_array(self.type, f"{output_path}/{filename}", mode="w")
        filenames.append(filename)

        if self.contact_area is not None:
            filename = f"{obj_idx}_{self.coll_obj}_{idx}_contact_area.bl2"
            blosc2.save_array(self.contact_area, f"{output_path}/{filename}", mode="w")
            filenames.append(filename)

        if self.force is not None:
            filename = f"{obj_idx}_{self.coll_obj}_{idx}_force.bl2"
            blosc2.save_array(self.force, f"{output_path}/{filename}", mode="w")
            filenames.append(filename)

        if self.coupling_data is not None:
            filename = f"{obj_idx}_{self.coll_obj}_{idx}_coupling_data.bl2"
            blosc2.save_array(self.coupling_data, f"{output_path}/{filename}", mode="w")
            filenames.append(filename)

        filepath = f"{obj_idx}_{self.coll_obj}_{idx}.tar.gz"
        with tarfile.open(f"{output_path}/{filepath}", mode="w:gz") as tar:
            for filename in filenames:
                tar.add(f"{output_path}/{filename}", filename)

        for filename in filenames:
            os.remove(f"{output_path}/{filename}")

        return filepath

@dataclass
class ScoreTrack:
    """Represents a score track for a single object."""
    obj_idx: int
    obj_name: str
    is_final: bool = False
    total_samples: int = None
    events: List[ScoreEvent] = field(default_factory=list)

    def add_event(self, event: ScoreEvent) -> None:
        """Add an event to the track."""
        self.events.append(event)

    def save(self, filepath: str) -> None:
        """
        Save the ScoreTrack to a tar gz file.

        Args:
            filepath: Path to save the file
            indent: JSON indentation level (None for compact format)
        """

        # make output path
        dirpath = os.path.dirname(filepath)
        output_path = f"{dirpath}/save"
        os.makedirs(output_path, exist_ok=True)

        score_track = {
            'obj_idx': self.obj_idx,
            'obj_name': self.obj_name,
            'is_final': self.is_final,
            'total_samples': self.total_samples
        }

        # Save score_track to file
        json_file = os.path.basename(filepath).removesuffix('tar.gz') + 'json'
        with open(f"{output_path}/{json_file}", 'w') as f:
            json.dump(score_track, f, indent=2)

        to_be_removed = [json_file]
        with tarfile.open(filepath, mode="w:gz") as tar:
            tar.add(f"{output_path}/{json_file}", json_file)
            for idx in range(len(self.events)):
                filename = self.events[idx].save(output_path, self.obj_idx, idx)
                tar.add(f"{output_path}/{filename}", filename)        
                to_be_removed.append(filename)

        for filename in to_be_removed:
            os.remove(f"{output_path}/{filename}")

    @classmethod
    def load(cls, filepath: str, final: bool = False) -> 'ScoreTrack':
        """
        Load a ScoreTrack from a tar gz file.

        Args:
            filepath: Path to the file to load

        Returns:
            Loaded ScoreTrack instance
        """
        events = []
        contact_area, force, coupling_data = (None for _ in range(3))

        # make output path
        dirpath = os.path.dirname(filepath)
        output_path = f"{dirpath}/extract"
        os.makedirs(output_path, exist_ok=True)
        
        to_be_removed = []
        with tarfile.open(filepath, mode="r:gz") as tar:
            filenames = tar.getnames()
            for filename in filenames:
               if filename.endswith('json'):
                   tar.extract(filename, output_path)
                   to_be_removed.append(filename)
                   with open(f"{output_path}/{filename}", 'r') as f:
                       score_track = json.load(f)
                       if final and not score_track['is_final']:
                           break
               elif filename.endswith('tar.gz'):
                   tar.extract(filename, output_path)
                   to_be_removed.append(filename)
                   with tarfile.open(f"{output_path}/{filename}", mode="r:gz") as score_event_tar:
                       event_files = score_event_tar.getnames()
                       for event_file in event_files:
                           if event_file.endswith('.json'):
                               score_event_tar.extract(event_file, output_path)
                               to_be_removed.append(event_file)
                               with open(f"{output_path}/{event_file}", 'r') as f:
                                   event_track = json.load(f)
                                   coll_obj = event_track['coll_obj']
                                   start_sample = event_track['start_sample']
                                   stop_sample = event_track['stop_sample']
#                       for event_file in event_files:
                           else:
                               score_event_tar.extract(event_file, output_path)
                               to_be_removed.append(event_file)
                               if event_file.endswith('b2'):
                                   cparams = blosc2.CParams(codec=blosc2.Codec.LZ4, typesize=1, clevel=1, nthreads=8)
                                   dparams = blosc2.DParams(nthreads=16)
                                   vertex_ids = blosc2.load(f"{output_path}/{event_file}", cparams=cparams, dparams=dparams)
                               elif event_file.endswith('bl2'):
                                   if 'type' in event_file:
                                       ev_type = blosc2.load_array(f"{output_path}/{event_file}")
                                   elif 'contact_area' in event_file:
                                       contact_area = blosc2.load_array(f"{output_path}/{event_file}")
                                   elif 'force' in event_file:
                                       force = blosc2.load_array(f"{output_path}/{event_file}")
                                   elif 'coupling_data' in event_file:
                                       coupling_data = blosc2.load_array(f"{output_path}/{event_file}")

                   events.append(ScoreEvent(coll_obj=coll_obj, start_sample=start_sample, stop_sample=stop_sample, type=ev_type, contact_area=contact_area, force=force, vertex_ids=vertex_ids, coupling_data=coupling_data))

        for file in to_be_removed:
            os.remove(f"{output_path}/{file}")
        score_track['events'] = events
        return cls(**score_track)
