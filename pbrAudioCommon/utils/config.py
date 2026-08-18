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

import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field

from ..lib.acoustic_shader import AcousticShader, AcousticProperties, AcousticCoefficients
from ..lib.frequency_response import SpatialFrequencyResponse

@dataclass
class SystemConfig:
    sample_rate: int = 48000
    bit_depth: int = 32
    fps: int = 24 # video fps
    fps_base: int = 1
    subframes: int = 1 # video subframes
    file_format: str = 'RAW'
    cache_path: str = "./pbrAudioCache/"
    # physicsSolver only
    collision_margin: float = 0.05
    samples_per_object: int = 1000
    hi_res_face2face: bool = False
    samples_per_face: int = 1000
    enable_denoiser: bool = False
    enable_trajectory_postprocess: bool = False
    # rigidBody only
    modal_modes: int = 20
    voxel_size: float = 0.001
    enable_postprocess: bool = False
    enable_proxy_synth: bool = False
    # pbrAudioRay only
    start_frame: int = None
    end_frame: int = None
    output_format: str = 'AMBISONIC'
    surround_format: str = None
    enable_vog: bool = False
    stereo_hrtf: bool = False
    render_path: str = "/tmp/"
    output_path: str = "/tmp/"
    number_of_rays: int = 16 # Number of rays to be emitted per entity
    direction_seed: int = 1 # Rays random isotropic direction seed
    bands_per_octave: float = 0 # frequency steps per octave
    lowest_frequency: float = 5
    higher_frequency: float = 24000.0 # Nyquist clock/2
    view_ray: bool = False
    # Debug
    debug: bool = False

@dataclass
class TrajectoryPostProcessConfig:
    # Detection parameters
    bounce_threshold: float = 0.001  # Minimum displacement for bounce detection (meters)
#    bounce_frequency_range: Tuple[float, float] = (50, 500)  # Hz range for bounce detection
#    penetration_margin: float = 0.001  # Margin for penetration detection (meters)
    # Correction parameters
    correction_strength: float = 0.8  # 0-1, how strongly to correct artifacts
    smoothing_sigma: float = 2.0  # Gaussian sigma for trajectory smoothing
    min_contact_duration: int = 5  # Minimum frames for contact detection
    # Physics constraints
    max_velocity_change: float = 10.0  # Maximum allowed velocity change (m/s² per frame)
    max_angular_velocity: float = 100.0  # Maximum angular velocity (rad/s)

@dataclass
class DenoiserConfig:
    # DC Offset Removal parameters
    enable_dc_blocker: bool = False
    dc_blocker_alpha: float = 0.999  # DC blocker coefficient (higher = more aggressive)
    # Adaptive Noise Gate parameters
    enable_noise_gate: bool = False
    gate_threshold_db: float = -60.0  # Noise gate threshold in dB
    gate_attack_ms: float = 2.0       # Attack time in ms
    gate_release_ms: float = 50.0     # Release time in ms
    gate_hold_ms: float = 10.0        # Hold time in ms
    # Temporal Smoothing parameters
    enable_temporal_smoothing: bool = False
    temporal_smoothing_window: int = 5  # Window size for temporal smoothing (samples)
    # Spectral Noise Reduction parameters
    enable_spectral_noise_reduction: bool = False
    spectral_fft_size: int = 2048      # FFT size for spectral processing
    spectral_hop_size: int = 512       # Hop size for spectral processing
    spectral_noise_floor_db: float = -80.0  # Noise floor estimate in dB
    spectral_reduction_strength: float = 0.8  # Reduction strength (0-1)
    spectral_smoothing: float = 0.3    # Spectral smoothing factor
    # Envelope Shaping parameters
    enable_envelope_shaping: bool = False
    envelope_attack_ms: float = 1.0    # Attack time for envelope
    envelope_release_ms: float = 20.0  # Release time for envelope
    envelope_smoothing: float = 0.5    # Envelope smoothing factor
    # Gaussian Adaptive Smoothing parameters
    enable_gaussian_adaptive_smoothing: bool = False
    gaussian_sigma_min: float = 0.5    # Minimum Gaussian sigma
    gaussian_sigma_max: float = 3.0    # Maximum Gaussian sigma
    gaussian_force_threshold: float = 0.1  # Force threshold for adaptive smoothing

@dataclass
class PostProcessConfig:
    """Configuration for post-processing parameters."""
    # Denoising parameters
    dynamic_denoise_enabled: bool = True
    noise_gate_threshold_db: float = -60.0
    noise_floor_estimate_db: float = -80.0
    spectral_reduction_strength: float = 0.7
    temporal_smoothing_window: int = 5
    # Dynamic reference weighting
    force_reference_weight: float = 0.3  # How much to trust force signals
    min_force_threshold: float = 1e-6    # Minimum force to consider active
    # Smoothing parameters
    smoothing_enabled: bool = True
    smoothing_window_ms: float = 2.0     # Window in milliseconds
    adaptive_smoothing: bool = True      # Smooth more during quiet sections
    # Phase alignment
    phase_align_enabled: bool = True
    crossfade_samples: int = 256         # Crossfade length for blending
    # Amplification
    target_rms: float = 0.15             # Target RMS level
    max_gain_db: float = 20.0            # Maximum gain in dB
    dynamic_range_compression: float = 0.5  # 0=no compression, 1=full
    # Blending
    blend_enabled: bool = True
    dry_wet_mix: float = 0.85            # 0=dry only, 1=wet only
    # Output
    normalize_output: bool = True
    # Debug
    verbose: bool = False

@dataclass
class AcousticDomainConfig:
    idx: int = 0
    name: str = "acoustic_domain"
    type: str = 'world'
    geometry: np.ndarray = field(default_factory=lambda: np.array([]))  #vertices array
    acoustic_shader: Optional[AcousticShader] = None

@dataclass
class SourceConfig:
    idx: int
    name: str
    type: str  # "spherical", "planar"
    static: bool
    size: float = None
    width: float = None
    height: float = None
    audio_file: str = None
    pose_path: str = None
    spatial_freq_response: Optional[SpatialFrequencyResponse] = None
    spatial_freq_response_file: Optional[str] = None
    acoustic_shader: Optional[AcousticShader] = None

@dataclass
class OutputConfig:
    idx: int
    name: str
    type: str  # "AMBI", "MONO"
    static: bool
    size: float = None
    order: int = None
    spatial_arrangement_file: str = None
    pose_path: str = None
    microphone_type: str = None # OMNIDIRECTIONAL, CARDIOID, HYPERCARDIOID, FIGURE_8
    spatial_freq_response: Optional[SpatialFrequencyResponse] = None
    spatial_freq_response_file: Optional[str] = None
    calibration: Optional[SpatialFrequencyResponse] = None
    calibration_file: Optional[str] = None

@dataclass
class ObjectConfig:
    idx: int
    name: str
    obj_path: str
    pose_path: str
    static: bool
    stochastic_variation: bool = False
    proxy_type: Union[bool, int] = False # 0 = octahedron, 1 = icosahedron for < blender.proxy_size_threshold, 2,3,4 for low,mid,hi manual selection and icosahedron subdivision, 6 = ConvexHull 
    min_detail_size: float = 0.01
    ground: bool = False
    resonance: bool = False
    resonance_modes: int = 10
    is_shard: Union[bool, int] = False
    fractured: Union[bool, int] = False
    shard: Union[bool, np.ndarray] = False # for shards of fractured object [obj_idx]
    connected: Union[bool, np.ndarray] = False # for static coupled systems [[obj_idx, coupling_strength]]
    acoustic_shader: Optional[AcousticShader] = None

@dataclass
class WavePropagationConfig:
    max_interactions: int = 8192
    enable_interface: bool = True
    enable_resonance: bool = True
    enable_termination: bool = True
    use_dispersion_correction: bool = True # account for variations in speed due to factors like temperature and wind in the medium
    dispersion_order: int = 2
    use_extended_reaction: bool = False # from RTS
    max_modal_reaction: int = 3
    use_complex_eigenray: bool = False # infrasound
    max_complex_eigenray: int = 3

@dataclass
class FDTDConfig:
    # placeholder config class for FDTD Shaders to Render
#    enable_damping: bool = True
#    damping_coefficient: float = 0.02
#    enable_boundary: bool = True
#    boundary_type: str = "open"
#    boundary_absorption: float = 1.0
#    interaction_threshold: float = 0.01
    courant_number: float = 0.5
    max_sound_speed: float = 500.0
    stability_margin: float = 0.9

@dataclass
class InterfaceConfig:
    enable_absorption: bool = True
    enable_reflection: bool = True
    max_reflection: int = 5
    enable_scattering: bool = True
    max_scattering: int = 5
    enable_transmission: bool = True
    max_transmission: float = 0.75
    enable_diffraction: bool = True
    max_diffraction: int = 5
    min_impedance_ratio: float = 0.1
    max_impedance_ratio: float = 10.0

@dataclass
class ResonanceConfig:
    max_structure_resonance_modes: int = 10 # extended reaction
    decay_time_constant: float = 0.99
    resonance_threshold: float = 0.1
    enable_helmholtz: bool = True
    min_cavity_volume: float = 0.001 # cubic meters
    min_cavity_size = 8  # Cavity detection parameters: Minimum voxels for cavity
    max_cavity_size = 1000  # Cavity detection parameters: Maximum voxels for cavity
    min_neck_ratio = 0.1  # Cavity detection parameters: Minimum neck-to-cavity size ratio
    enable_parallel_wall: bool = True
    min_wall_distance: float = 0.5  # meters
    max_wall_distance: float = 20.0  # meters
    min_room_volume: float = 1.0 # cubic meters
    max_resonance_room_modes: int = 10
    enable_tube: bool = True
    min_tube_length: float = 0.3  # meters
    max_tube_length: float = 10.0  # meters
    min_tube_aspect_ratio: float = 3.0  # length/width ratio for tubes
    max_tube_cross_section: float = 1.0  # square meters

@dataclass
class TerminationConfig:
    termination_type: str = "reverberation_time"  # "reverberation_time", "energy_threshold"
    # reverberation_time
    reverberation_time: float = 2.0
    # energy_threshold
    energy_threshold: float = 120 # Minimum energy to terminate
    # minimum active rays number
    min_rays_number: int = 3

@dataclass
class AudioRecorderConfig:
    output_format: str = "npz" # npz, wav
    path: str = "./exports/audio/"

@dataclass
class AmbisonicRenderConfig:
    file_format: str = "wav" # bwf, wav
    order: int = 1
    sample_rate: int = 48000 # it's needed?
    bit_depth: int = 32 # it's needed?
    path: str = "./exports/ambisonic/"

class Config:
    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
            self.data = json.load(f)

        self.system = SystemConfig(**self.data.get('system', {}))
        self.trajectory_postprocess = TrajectoryPostProcessConfig(**self.data.get('trajectory_postprocess', {}))
        self.denoiser = DenoiserConfig(**self.data.get('denoiser', {}))
        self.postprocess = PostProcessConfig(**self.data.get('postprocess', {}))
        self.wave_propagation = WavePropagationConfig(**self.data.get('wave_propagation', {}))
        self.fdtd = FDTDConfig(**self.data.get('fdtd', {}))
        self.interface = InterfaceConfig(**self.data.get('interface', {}))
        self.resonance = ResonanceConfig(**self.data.get('resonance', {}))
        self.termination = TerminationConfig(**self.data.get('termination', {}))
        self.audio_recorder = AudioRecorderConfig(**self.data.get('audio_recorder', {}))
        self.ambisonic_render = AmbisonicRenderConfig(**self.data.get('ambisonic_render', {}))

        # Handle acoustic domain with nested acoustic_shader
        acoustic_domain_data = self.data.get('acoustic_domain', {})
        acoustic_shader_data = acoustic_domain_data.get('acoustic_shader', {})
        self.acoustic_domain = AcousticDomainConfig(
            **{k: v for k, v in acoustic_domain_data.items() if k != 'acoustic_shader'},
            acoustic_shader=self._create_acoustic_shader(acoustic_shader_data) if acoustic_shader_data else None
        )

        # Handle sources with nested acoustic_shader and spatial_freq_response
        self.sources = []
        for s in self.data.get('sources', []):
            acoustic_shader_data = s.get('acoustic_shader', {})
            spatial_freq_response_data = s.get('spatial_freq_response', {})
            source_config = SourceConfig(
                **{k: v for k, v in s.items() if k not in ['acoustic_shader', 'spatial_freq_response']},
                acoustic_shader=self._create_acoustic_shader(acoustic_shader_data) if acoustic_shader_data else None,
                spatial_freq_response=self._create_spatial_freq_response(spatial_freq_response_data) if spatial_freq_response_data else None
            )
            self.sources.append(source_config)

        # Handle outputs with nested spatial_freq_response and calibration
        self.outputs = []
        for o in self.data.get('outputs', []):
            spatial_freq_response_data = o.get('spatial_freq_response', {})
            calibration_data = o.get('calibration', {})
            output_config = OutputConfig(
                **{k: v for k, v in o.items() if k not in ['spatial_freq_response', 'calibration']},
                spatial_freq_response=self._create_spatial_freq_response(spatial_freq_response_data) if spatial_freq_response_data else None,
                calibration=self._create_spatial_freq_response(calibration_data) if calibration_data else None
            )
            self.outputs.append(output_config)


        # Handle objects with nested acoustic_shader
        self.objects = []
        for o in self.data.get('objects', []):
            acoustic_shader_data = o.get('acoustic_shader', {})
            object_config = ObjectConfig(
                **{k: v for k, v in o.items() if k != 'acoustic_shader'},
                acoustic_shader=self._create_acoustic_shader(acoustic_shader_data) if acoustic_shader_data else None
            )
            self.objects.append(object_config)

    def _create_acoustic_shader(self, shader_data: Dict[str, Any]) -> AcousticShader:
        """Create AcousticShader instance from dictionary data"""
        acoustic_props_data = shader_data.get('acoustic_properties', {})

        # Create AcousticCoefficients for each property
        acoustic_properties = AcousticProperties()

        if 'absorption' in acoustic_props_data:
            abs_data = acoustic_props_data['absorption']
            if isinstance(abs_data, float):
                frequencies = np.linspace(shader_data.get('low_frequency', 1.0), shader_data.get('high_frequency', 24000.0), 5)
                abs_data = [abs_data for _ in range(5)]
                abs_data = {"frequencies": frequencies, "coefficients": abs_data, "phases": []}
            acoustic_properties.absorption = AcousticCoefficients(
                frequencies=np.array(abs_data['frequencies']),
                coefficients=np.array(abs_data['coefficients'])
            )

        if 'transmission' in acoustic_props_data:
            refr_data = acoustic_props_data['transmission']
            if isinstance(refr_data, float):
                frequencies = np.linspace(shader_data.get('low_frequency', 1.0), shader_data.get('high_frequency', 24000.0), 5)
                refr_data = [refr_data for _ in range(5)]
                refr_data = {"frequencies": frequencies, "coefficients": refr_data, "phases": []}
            acoustic_properties.transmission = AcousticCoefficients(
                frequencies=np.array(refr_data['frequencies']),
                coefficients=np.array(refr_data['coefficients'])
            )

        if 'reflection' in acoustic_props_data:
            refl_data = acoustic_props_data['reflection']
            if isinstance(refl_data, float):
                frequencies = np.linspace(shader_data.get('low_frequency', 1.0), shader_data.get('high_frequency', 24000.0), 5)
                refl_data = [refl_data for _ in range(5)]
                refl_data = {"frequencies": frequencies, "coefficients": refl_data, "phases": []}
            acoustic_properties.reflection = AcousticCoefficients(
                frequencies=np.array(refl_data['frequencies']),
                coefficients=np.array(refl_data['coefficients'])
            )

        if 'scattering' in acoustic_props_data:
            scat_data = acoustic_props_data['scattering']
            if isinstance(scat_data, float):
                frequencies = np.linspace(shader_data.get('low_frequency', 1.0), shader_data.get('high_frequency', 24000.0), 5)
                scat_data = [scat_data for _ in range(5)]
                scat_data = {"frequencies": frequencies, "coefficients": scat_data, "phases": []}
            acoustic_properties.scattering = AcousticCoefficients(
                frequencies=np.array(scat_data['frequencies']),
                coefficients=np.array(scat_data['coefficients'])
            )

        # Create AcousticShader
        return AcousticShader(
            sound_speed=shader_data.get('sound_speed', 343.0),
            young_modulus=shader_data.get('young_modulus', []),
            poisson_ratio=shader_data.get('poisson_ratio', []),
            density=shader_data.get('density', 1.225),
            damping=shader_data.get('damping', []),
            friction=shader_data.get('friction', []),
            roughness=shader_data.get('roughness', []),
            temperature=shader_data.get('temperature', []),
            impedence=shader_data.get('impedence', []),
            low_frequency=shader_data.get('low_frequency', 1.0),
            high_frequency=shader_data.get('high_frequency', 24000.0),
            failure_stress=shader_data.get('failure_stress', []),
            acoustic_properties=acoustic_properties
        )

    def _create_spatial_freq_response(self, response_data: Dict[str, Any]) -> SpatialFrequencyResponse:
        """Create SpatialFrequencyResponse instance from dictionary data"""
        return SpatialFrequencyResponse(
            azimuths=np.array(response_data.get('azimuths', [])),
            elevations=np.array(response_data.get('elevations', [])),
            frequencies=np.array(response_data.get('frequencies', [])),
            magnitude=np.array(response_data.get('magnitude', [])),
            phases=np.array(response_data.get('phases', [])) if 'phases' in response_data else None
        )
