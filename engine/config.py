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
import json
import pathlib
import bpy
import aud
import zarr
import zarrs
import numpy as np

zarr.config.set({"codec_pipeline.path": "zarrs.ZarrsCodecPipeline"})

class pbrAudioConfigInit:
    def __init__(self):
        """Initialize self var"""
        self.scene = bpy.context.scene
        self.fps = self.scene.render.fps/self.scene.render.fps_base
        self.sample_rate = self.scene.pbraudio.sample_rate
        self.spf = self.sample_rate/self.fps         # sample per frame
        self.current_frame = self.scene.frame_current
        self.sample_start = int(self.spf*(self.current_frame-1))
        self.sample_stop = int(self.spf*(self.current_frame))
        if self.scene.pbraudio.cache_path:
            self.true_path = self.scene.pbraudio.cache_path + 'pbrAudioCache'
        else:
            self.true_path = '//pbrAudioCache'
        self.cache_path = bpy.path.abspath(self.true_path) #os.listdir(cachePath)
        # create config_{current_frame}.json
        self.config_file = os.path.join(self.cache_path, 'config', 'config' + str(f"{self.current_frame:05d}") + '.json')
        self.config = []

        self.domain_name = ''
        self.sound_speed = 343.4      # default to air @ ~20°C
        self.impedence = 413.5        # default to air @ ~20°C

        self.soxel_size = self.sound_speed/self.sample_rate

        self.output_dir = os.path.join(self.cache_path, 'output') 
        self.sound_dir = os.path.join(self.cache_path, 'sound')
        self.location_dir = os.path.join(self.cache_path, 'location')
        self.rotation_dir = os.path.join(self.cache_path, 'rotation')

    # create cache tree
    def create_cache(self):

        if not os.path.isdir(self.cache_path):
            os.makedirs(self.cache_path)
            for dir in 'config', 'location', 'rotation', 'obj', 'sound', 'output', 'zarr':
                subdir = os.path.join(self.cache_path, dir)
                os.makedirs(subdir)
        else:
            for dir in 'config', 'location', 'rotation', 'obj', 'sound', 'output', 'zarr':
                subdir = os.path.join(self.cache_path, dir)
                if not os.path.isdir(self.cache_path):
                    os.makedirs(subdir)

    def domain_config(self):
        pbrAudioType = 'domain'
        # find world domain property
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio'):
                if hasattr(world.pbraudio, 'acoustic_domain'):
                    acoustic_domain = world.pbraudio.acoustic_domain
                    self.domain_name = world.pbraudio.acoustic_domain.name
                    if not world.pbraudio.sound_speed == 0:
                        self.sound_speed = world.pbraudio.sound_speed
                    if not world.pbraudio.impedence == 0:
                        self.impedence = world.pbraudio.impedence
        #            medium_type = world.pbraudio.type
        #            density = world.pbraudio.density
        #            temperature = world.pbraudio.temperature
                    self.soxel_size = self.sound_speed/self.sample_rate

                    vertexs = acoustic_domain.bound_box
                    # find distance of corner vertex of domain bounding box
                    f = vertexs[4][0] - vertexs[0][0]
                    g = vertexs[3][1] - vertexs[0][1]
                    h = vertexs[1][2] - vertexs[0][2]
                    # find number of cells in domain bounding box
                    i = int(f/self.soxel_size)
                    j = int(g/self.soxel_size)
                    k = int(h/self.soxel_size)


                    cfg = {
                        'type': pbrAudioType,
                        'data': {
                            'name': self.domain_name,
                            'pbrAudioData': {
                                'sample_rate': self.sample_rate,
                                'sound_speed': self.sound_speed,
                                'impedence': self.impedence
                                },
                            'file_path': os.path.join(self.cache_path, 'zarr'),
                            'shape': (i,j,k),
                        }
                    }
                    self.config.append(cfg)


    def source_config(self):
        # find sources
        pbrAudioType = 'source'
        for source in bpy.data.objects:
            if hasattr(source.pbraudio, 'source'):
                if source.pbraudio.source:
                    name = source.name

                    # init ndarray for location and rotation
                    #location = np.ndarray(shape=(0,3), dtype=np.float32, order='C')
                    location = np.ndarray(shape=(0,3), dtype=np.int64, order='C')
                    rotation = np.ndarray(shape=(0,4), dtype=np.float32, order='C')

                    # convert sound file to ndarray
                    path = pathlib.PurePosixPath(bpy.path.abspath(source.pbraudio.source.filepath))
                    if not self.scene.pbraudio.cache_status:
                        sound = aud.Sound.file(path.as_posix())
                        sound = sound.resample(self.sample_rate, 4)
                        sound = sound.data()

                    source_type = source.pbraudio.source_type

                    for spf_num in range(self.sample_start, self.sample_stop):
                        subframe = spf_num/self.spf
                        self.scene.frame_set(frame=self.current_frame, subframe=subframe)
                        #sample_num = current_frame*subframe_rate + subframe_num          # or current_frame -1 ?

                        source_x = int(source.location[0]/self.soxel_size)
                        source_y = int(source.location[0]/self.soxel_size)
                        source_z = int(source.location[0]/self.soxel_size)
                        source_xyz = [source_x, source_y, source_z]

                        location = np.insert(location, spf_num, source_xyz, axis=0)
                        rotation = np.insert(rotation, spf_num, source.rotation_quaternion, axis=0)

                    # save any sources sound file, location, rotation as np.ndarray
                    location_filename = name + '_' + str(f"{self.current_frame:05d}") + '.npz'
                    rotation_filename = name + '_' + str(f"{self.current_frame:05d}") + '.npz'
                    sound_filename = name + '_' + path.stem + '.npz'
                    
                    location_npz = os.path.join(self.location_dir, location_filename)
                    rotation_npz = os.path.join(self.rotation_dir, rotation_filename)
                    sound_npz = os.path.join(self.sound_dir, sound_filename)

                    np.savez_compressed(location_npz, array1=location)
                    np.savez_compressed(rotation_npz, array1=rotation)
                    if not self.scene.pbraudio.cache_status:
                        np.savez_compressed(sound_npz, array1=sound)

                    cfg = {
                        'type': pbrAudioType,
                        'data': {
                            'name': name,
                            'pbrAudioData': source_type,
                            'file_path': sound_npz,
                            'location': location_npz,
                            'rotation': rotation_npz
                        }
                    }
                    self.config.append(cfg)


    def output_config(self):
        # find outputs
        pbrAudioType = 'output'
        for output in bpy.data.objects:
            if hasattr(output.pbraudio, 'output'):
                if output.pbraudio.output:
                    name = output.name

                    order = 0
                    type = output.pbraudio.output_type
                    if type == 'AMBI':
                        order = int(output.pbraudio.ambisonic_order)

                    # save any output sound file, location, rotation as np.ndarray
                    channels = (order+1)**2
                    output_sound = np.ndarray((0,channels), dtype=np.float32)

                    # append ndarray with interpolated animation for subframe
                    location = np.ndarray(shape=(0,3), dtype=np.int64, order='C')
                    rotation = np.ndarray(shape=(0,4), dtype=np.float32, order='C')

                    for spf_num in range(self.sample_start, self.sample_stop):
                        subframe = spf_num/self.spf
                        self.scene.frame_set(frame=self.current_frame, subframe=subframe)
                        #sample_num = current_frame*subframe_rate + subframe_num          # or current_frame -1 ?
                        #sample_num = scene.frame_current_final

                        output_x = int(output.location[0]/self.soxel_size)
                        output_y = int(output.location[0]/self.soxel_size)
                        output_z = int(output.location[0]/self.soxel_size)
                        output_xyz = [output_x, output_y, output_z]

                        location = np.insert(location, spf_num, output_xyz, axis=0)
                        rotation = np.insert(rotation, spf_num, output.rotation_quaternion, axis=0)

                    location_filename = name + '_' + str(f"{self.current_frame:05d}") + '.npz'
                    rotation_filename = name + '_' + str(f"{self.current_frame:05d}") + '.npz'
                    output_filename = name + '_' + str(f"{channels:05d}") + '.npz'

                    location_npz = os.path.join(self.location_dir, location_filename)
                    rotation_npz = os.path.join(self.rotation_dir, rotation_filename)
                    output_npz = os.path.join(self.output_dir, output_filename)

                    np.savez_compressed(location_npz, array1=location)
                    np.savez_compressed(rotation_npz, array1=rotation)
                    np.savez_compressed(output_npz, array1=output_sound)

                    cfg = {
                        'type': pbrAudioType,
                        'data': {
                            'name': name,
                            'pbrAudioData': order,
                            'file_path': output_npz,
                            'location': location_npz,
                            'rotation': rotation_npz
                        }
                    }
                    self.config.append(cfg)

    def create_config(self):
        js = json.dumps(self.config, sort_keys=True, indent=4, separators=(',', ': '))
        with open(self.config_file, 'w+') as json_file:
            json_file.write(js)

    def initZarr(self):
        # init zarr store
        zarrPath = os.path.join(self.cache_path, 'zarr', self.domain_name)
        compressors = zarr.codecs.BloscCodec(cname='blosclz', clevel=3, shuffle=zarr.codecs.BloscShuffle.bitshuffle)
        zarr_acoustic = zarr.create_group(store=zarrPath)

        # init zarr domain (global)
        for index in range(len(self.config)):
            if self.config[index]['type'] == 'domain':
                i = self.config[index]['data']['shape'][0]
                j = int(self.config[index]['data']['shape'][1])
                k = int(self.config[index]['data']['shape'][2])

        zarr_acoustic_global = zarr_acoustic.create_group('global')
        impedence = zarr_acoustic_global.create_array(name='impedence', shape=(i, j, k), shards=(128, 128, 128), chunks=(32, 32, 32), dtype='uint16', fill_value=self.impedence, compressors=compressors)
        sound_speed = zarr_acoustic_global.create_array(name='sound_speed', shape=(i, j, k), shards=(128, 128, 128), chunks=(32, 32, 32), dtype='uint16', fill_value=self.sound_speed, compressors=compressors)

        # init zarr sources (local)
        zarr_acoustic_local = zarr_acoustic.create_group('local')
        # for any sound sources create new group layer and mark the first sample ToDo
        for index in range(len(self.config)):
            if self.config[index]['type'] == 'source':
                source_xyz = np.load(self.config[index]['data']['location'])
                source_array = np.load(self.config[index]['data']['file_path'])
                f, g, h = source_xyz['array1'][0]

                zarr_name = 'layer_' + self.config[index]['data']['name']
                zarr_layer  = zarr_acoustic_local.create_group(zarr_name)
                # for any layer create a subgroup with soxel, direction and sample_ref (reference audio sample number) array
                zarr_zero  = zarr_layer.create_group('0')
                soxel = zarr_zero.create_array(name='soxel', shape=(i, j, k), shards=(128, 128, 128), chunks=(32, 32, 32), dtype='float32', fill_value=0.0, compressors=compressors)
                soxel[f,g,h] = source_array['array1'][0][0]
                direction = zarr_zero.create_array(name='direction', shape=(i, j, k), shards=(128, 128, 128), chunks=(32, 32, 32), dtype='uint8', fill_value=255, compressors=compressors)
                direction[f,g,h] = 128
                sample_ref = zarr_zero.create_array(name='sample_ref', shape=(i, j, k), shards=(128, 128, 128), chunks=(32, 32, 32), dtype='uint32', fill_value=0, compressors=compressors)


    def end_init(self):
        self.scene.frame_set(frame=self.current_frame)


'''
    def object_config(self):
        bpy.ops.wm.obj_export(filepath="", check_existing=True, filter_blender=False,
                              filter_backup=False, filter_image=False, filter_movie=False,
                              filter_python=False, filter_font=False, filter_sound=False,
                              filter_text=False, filter_archive=False, filter_btx=False,
                              filter_collada=False, filter_alembic=False, filter_usd=False,
                              filter_obj=False, filter_volume=False, filter_folder=True,
                              filter_blenlib=False, filemode=8, display_type='DEFAULT',
                              sort_method='DEFAULT', export_animation=False,
                              start_frame=-2147483648, end_frame=2147483647,
                              forward_axis='NEGATIVE_Z', up_axis='Y', global_scale=1,
                              apply_modifiers=True, export_eval_mode='DAG_EVAL_VIEWPORT',
                              export_selected_objects=True, export_uv=False, export_normals=False,
                              export_colors=False, export_materials=False, export_pbr_extensions=False,
                              path_mode='AUTO', export_triangulated_mesh=True,
                              export_curves_as_nurbs=False, export_object_groups=False,
                              export_material_groups=False, export_vertex_groups=False,
                              export_smooth_groups=False, smooth_group_bitflags=False,
                              filter_glob="*.obj;*.mtl", collection="")

        # select object inside and intersecting domain
        domain = bpy.data.objects[domainName]  # Replace with your domain object name
        for obj in bpy.context.scene.objects:
            if domain.bound_box[0][0] <= obj.location.x <= domain.bound_box[4][0] and \
               domain.bound_box[0][1] <= obj.location.y <= domain.bound_box[2][1] and \
               domain.bound_box[0][2] <= obj.location.z <= domain.bound_box[1][2]:
                obj.select_set(True)


                    cfg = {
                        'type': pbrAudioType,
                        'data': {
                            'name': name,
                            'pbrAudioData': {
                                'sample_rate': sample_rate,
                                'sound_speed': sound_speed,
                                'impedence': impedence
                                },
                            'file_path': os.path.join(cache_path, 'zarr'),
                            'shape': (i,j,k),
                        }
                    }
                    self.config.append(cfg)

                    cfg = {
                        'type': pbrAudioType,
                        'data': {
                            'name': name,
                            'pbrAudioData': pbrAudioData,
                            'file_path': sound_npz,
                            'location': location_npz,
                            'rotation': rotation_npz
                        }
                    }
                    self.config.append(cfg)


'''
