import os
import re
import random
import string
import trimesh
import numpy as np
import numba as nb
import resampy
import soundfile as sf
from typing import Any, Tuple, Optional, List, Union, Dict

from ..lib.filter import LinkwitzRileyFilter

def _mesh_to_obj(vertices: np.ndarray, normals: np.ndarray, faces: np.ndarray, obj_file: str, resonance: bool = False):
    """
    Convert an npz mesh file to Wavefront OBJ format.
    
    Args:
        vertices: numpy array with indexed vertices
        normals: numpy array with vertex normals
        faces: numpy array with faces indices
        obj_file: Path where the output .obj file will be saved
    """
    # Create trimesh object
    mesh = trimesh.Trimesh(vertices=vertices, vertex_normals=normals, faces=faces)

    # Create simplified convex hull for resonance model
    if resonance:
        try:
            simplified = mesh.simplify_quadric_decimation(percent=0.5, aggression=0)
            if simplified.is_volume and simplified.is_watertight and simplified.is_winding_consistent:
                simplified.export(f"{obj_file.removesuffix('.obj')}_resonance.obj", include_normals=True, file_type='obj')
        except: 
            pass

    # Export as obj
    mesh.export(obj_file, file_type='obj')
    return

def _acoustic_domain_mesh(config: Any) -> trimesh.Trimesh:
    """ Return the AcousticDomain as mesh """
    ac_geometry = np.array(config.acoustic_domain.geometry)
    ac_max = np.array([max(ac_geometry[i][0] for i in range(len(ac_geometry))), max(ac_geometry[i][1] for i in range(len(ac_geometry))), max(ac_geometry[i][2] for i in range(len(ac_geometry)))])
    ac_min = np.array([min(ac_geometry[i][0] for i in range(len(ac_geometry))), min(ac_geometry[i][1] for i in range(len(ac_geometry))), min(ac_geometry[i][2] for i in range(len(ac_geometry)))])
    ac = trimesh.creation.box(bounds=(ac_min,ac_max))
    return ac

def _load_mesh(obj_config: Any, frame_idx: int, use_proxy_path: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load mesh for an object at a given frame index."""
    if obj_config.static:
        # For static, load once
        filename = obj_config.obj_path
        if use_proxy_path and obj_config.proxy_type is not False:
            filename = f"{obj_config.obj_path}/proxy"
        # Assume single npz file or directory with one file
        if os.path.isdir(obj_config.obj_path):
            files = [f for f in os.listdir(obj_config.obj_path) if f.endswith('.npz')]
            filename = os.path.join(obj_config.obj_path, files[0])
        else:
            filename = obj_config.obj_path
    else:
        # For dynamic, load sequence
        obj_path = obj_config.obj_path
        if use_proxy_path and obj_config.proxy_type is not False:
            obj_path = f"{obj_config.obj_path}/proxy"
        items = os.listdir(obj_path)
        items = [x for x in items if x.endswith('.npz')]
        filenames = sorted(items, key=lambda x: int(''.join(filter(str.isdigit, x))))
        filename = os.path.join(obj_path, filenames[frame_idx])

    data = np.load(filename, allow_pickle=False)
    vertices = data[data.files[0]]
    normals = data[data.files[1]]
    faces = data[data.files[2]]
    return vertices, normals, faces

def _load_pose(config_obj: Any) -> Tuple[np.ndarray, np.ndarray]:
    """Load all pose sequence for an object."""
    for obj_type in ['SourceConfig', 'OutputConfig', 'ObjectConfig']:
        if obj_type in str(type(config_obj)):
            type_error = False
            pose_path = config_obj.pose_path
            obj_name = config_obj.name

            npz_file = os.path.join(pose_path, f"{obj_name}.npz")

            if not npz_file:
                raise ValueError(f"No pose files found for {obj_name} in {pose_path}")

            pose = np.load(npz_file)
            positions = pose[pose.files[0]]
            rotations = pose[pose.files[1]]
            break
        else:
            type_error = True

    if type_error:
        raise ValueError(f"{config_obj} is not of know type: SourceConfig, OutputConfig, ObjectConfig.")
    else:
        return positions, rotations

def _generate_band_frequencies(lowest_frequency: float, higher_frequency: float, bands_per_octave: float):
    """
    Generate frequencies from lowest_frequency to higher_frequency with specified steps per octave
    """
    frequencies = []
    current_freq = lowest_frequency
    
    if bands_per_octave > 0:
        # Calculate the frequency ratio for one step
        step_ratio = 2 ** (1 / bands_per_octave)

        while current_freq <= higher_frequency:
            frequencies.append(current_freq)
            current_freq *= step_ratio
    else:
        frequencies.append(current_freq)

    return frequencies

def _euler_to_rotation_matrix(q: np.ndarray, degrees=False):
    """
    Convert Euler angles to rotation matrix (ZYX convention).
   
    Parameters:
    -----------
    q : np.ndarray
        yaw, pitch, roll
        yaw : float
            Rotation around Z axis (yaw)
        pitch : float
            Rotation around Y axis (pitch)
        roll : float
            Rotation around X axis (roll)
    degrees : bool, optional
        If True, input angles are in degrees. Default is False (radians).

    Returns:
    --------
    R : np.ndarray
        3x3 rotation matrix
    """
    roll, pitch, yaw = q

    if degrees:
        # Convert degrees to radians
        yaw = np.radians(yaw)
        pitch = np.radians(pitch)
        roll = np.radians(roll)

    # Precompute trigonometric functions
    cy = np.cos(yaw)
    sy = np.sin(yaw)
    cp = np.cos(pitch)
    sp = np.sin(pitch)
    cr = np.cos(roll)
    sr = np.sin(roll)

    # ZYX rotation matrix (R = Rz(yaw) * Ry(pitch) * Rx(roll))
    R = np.array([
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr]
    ])

    return R


def _parse_lib(lib_content: str):
    """
    Parse mesh2faust .lib file content

    Args:
        lib_content: String content of the .lib file

    Returns:
        Dictionary with modal parameters
    """
    freq_pattern = r'modeFreqsUnscaled.*?=.*?ba\.take.*?$$(.*?)$$'
    t60_pattern = r'modesT60s.*?=.*?t60Scale.*?ba\.take.*?$$(.*?)$$'
    gain_pattern = r'modesGains.*?=.*?waveform\{(.*?)\}'
    parentesis_match = r'\(([^()]+)\)'
    tuple_match = r'\d+\.?\d+'

    with open(lib_content, 'r') as file:
        lines = file.readlines()
        frequencies, t60s, gains = ([] for _ in range(3))
        for line in lines:
            line = line.replace('-nan','1')
            # Extract frequencies from modeFreqsUnscaled
            freq_match = re.search(freq_pattern, line, re.DOTALL)
            if not freq_match == None:
                freq_tuple_match = re.findall(tuple_match, freq_match.group())
                if not len(freq_tuple_match) == 0:
                    frequencies = [float(f) for f in freq_tuple_match]
                    break
                else:
                    frequencies = [1.0]
                    break
        for line in lines:
            # Extract T60 values
            t60_match = re.search(t60_pattern, line, re.DOTALL)
            if not t60_match == None:
                t60_par_match = re.findall(parentesis_match, t60_match.group())
                if not t60_par_match == None:
                    try:
                        t60_tuple_match = re.findall(tuple_match, t60_par_match[1])
                        if not t60_tuple_match == None:
                            t60s = [float(f) for f in t60_tuple_match]
                            break
                    except:
                        t60s = [1.0]
                        break
        for line in lines:
            # Extract nExPos
            nExPos_match = r'nExPos.*?=\s*(\d+)'
            nExPos = re.match(nExPos_match, line, re.DOTALL)
            if not nExPos == None:
                nExPos_pattern = r'\s*(\d+)'
                nExPos = re.search(nExPos_pattern, nExPos.group())
                if not nExPos == None:
                    nExPos = int(nExPos.group())
                    break
        for line in lines:
            # Extract gains - this is complex due to the large waveform
            gain_match = re.search(gain_pattern, line, re.DOTALL)
            if not gain_match == None:
                gain_tuple_match = re.findall(gain_pattern, gain_match.group())
                gain_tuple_match = re.sub("'", "", gain_tuple_match[0])
                if not gain_tuple_match == None:
                    try:
                        gains = [float(f) for f in gain_tuple_match.split(",")]
                    except:
                        gains = [1.0 for _ in range(nExPos)]
                        break

    return {
        'frequencies': np.array(frequencies),
        't60s': np.array(t60s),
        'gains': np.hsplit(np.array(gains), len(gains)/len(frequencies)),
        'nModes': len(frequencies)
    }

def _update_status(file_path: str, progress: Optional[int] = None):
    with open(file_path, 'w') as file:
        if not progress == None:
            file.write(f"{progress}")

def _cartesian_to_spherical(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """
    Convert cartesian coordinates to spherical coordinates.

    Args:
        x, y, z: Cartesian coordinates

    Returns:
        (azimuth, elevation, radius) in degrees and units
    """
    radius = np.sqrt(x*x + y*y + z*z)

    if radius == 0:
        return 0.0, 0.0, 0.0

    azimuth = np.arctan2(y, x)
    elevation = np.arcsin(z / radius)

    return azimuth, elevation, radius

@nb.jit(nopython=True)
def _trilinear_interpolate(field: np.ndarray, position: Tuple[float, float, float]) -> float:
    """Fast trilinear interpolation using numba"""
    i, j, k = position
   
    i0, j0, k0 = int(np.floor(i)), int(np.floor(j)), int(np.floor(k))
    i1, j1, k1 = i0 + 1, j0 + 1, k0 + 1
   
    # Check bounds
    if (i0 < 0 or i1 >= field.shape[0] or
        j0 < 0 or j1 >= field.shape[1] or
        k0 < 0 or k1 >= field.shape[2]):
        return 0.0
   
    # Calculate interpolation weights
    di, dj, dk = i - i0, j - j0, k - k0
    di1, dj1, dk1 = 1.0 - di, 1.0 - dj, 1.0 - dk

    # Get the 8 corner values
    v000 = field[i0, j0, k0]
    v001 = field[i0, j0, k1]
    v010 = field[i0, j1, k0]
    v011 = field[i0, j1, k1]
    v100 = field[i1, j0, k0]
    v101 = field[i1, j0, k1]
    v110 = field[i1, j1, k0]
    v111 = field[i1, j1, k1]

    # Trilinear interpolation
    c00 = v000 * di1 + v100 * di
    c01 = v001 * di1 + v101 * di
    c10 = v010 * di1 + v110 * di
    c11 = v011 * di1 + v111 * di

    c0 = c00 * dj1 + c10 * dj
    c1 = c01 * dj1 + c11 * dj

    value = c0 * dk1 + c1 * dk

    return value

def _degrees_to_radians(phase_coeffs, input_unit='auto'):
    """
    Verify if phase coefficients are in normalized radians and convert if needed.

    Parameters:
    -----------
    phase_coeffs : np.array
        Array of phase coefficients
    input_unit : str, optional
        Input unit type: 'radians', 'degrees', 'gradians', or 'auto' (default)
        If 'auto', the function will attempt to detect the unit

    Returns:
    --------
    normalized_phase : np.array
        normalized_phase : phase coefficients in normalized radians [-π, π]
    """
    # Make a copy to avoid modifying the original array
    phase = phase_coeffs.copy()
    was_normalized = False

    if input_unit == 'auto':
        # Auto-detection logic
        max_abs = np.max(np.abs(phase))

        if max_abs <= np.pi:
            # Likely already in radians
            original_unit = 'radians'
        elif max_abs <= 180:
            # Likely in degrees
            original_unit = 'degrees'
            was_normalized = True
        elif max_abs > 180:
            # Likely in gradians
            original_unit = 'gradians'
            was_normalized = True
        else:
            # Default to radians if uncertain
            original_unit = 'radians'
            print("Error: Could not auto-detect unit with certainty.")
            return None
    else:
        original_unit = input_unit
        was_normalized = (input_unit != 'radians')

    # Perform conversion if needed
    if original_unit == 'degrees':
        # Convert degrees to radians
        phase = np.deg2rad(phase)
        was_normalized = True
    elif original_unit == 'gradians':
        # Convert gradians to radians (200 gradians = 180 degrees = π radians)
        phase = phase * (np.pi / 200)
        was_normalized = True

    # Normalize to [-π, π] range
    if was_normalized or input_unit == 'radians':
        phase = np.mod(phase + np.pi, 2 * np.pi) - np.pi

    return phase

def _compute_rayleigh_damping(f1: float, f2: float, xi1: float, xi2: float = None) -> Tuple[float, float]:
    """
    Compute Rayleigh damping coefficients α and β.

    Parameters:
    -----------
    f1 : float
        First frequency (Hz)
    f2 : float
        Second frequency (Hz)
    xi1 : float
        Damping ratio at f11 (dimensionless, e.g., 0.05 for 5%)
    xi2 : float
        Damping ratio at f2 (dimensionless, e.g., 0.05 for 5%)

    Returns:
    --------
    tuple : (alpha, beta)
        Mass-proportional coefficient α (1/s)
        Stiffness-proportional coefficient β (s)

    Notes:
    ------
    Rayleigh damping: C = αM + βK
    Damping ratio at frequency ω: ξ = α/(2ω) + βω/2
    """
    xi2 = xi1 if xi2 == None else xi2

    # Convert frequencies to angular frequencies (rad/s)
    omega1 = 2 * np.pi * f1
    omega2 = 2 * np.pi * f2

    # Solve the system of equations:
    # ξ1 = α/(2ω1) + βω1/2
    # ξ2 = α/(2ω2) + βω2/2

    # Create the coefficient matrix
    A = np.array([
        [1/(2*omega1), omega1/2],
        [1/(2*omega2), omega2/2]
    ])

    # Create the right-hand side vector
    b = np.array([xi1, xi2])

    # Solve for α and β
    try:
        alpha, beta = np.linalg.solve(A, b)
        return alpha, beta
    except np.linalg.LinAlgError:
        raise ValueError("The two frequencies must be different to compute unique Rayleigh damping coefficients.")

def _mono_to_bands(audio_file: str, sample_rate: int, frequency_bands: List[Tuple[float, float]]) -> List:
    """
    Convert audio_file to frequency dependent np.ndarray in npz file audio_npz.
    """
    # Read the audio file
    try:
        audio_data, sr = sf.read(audio_file)
    except Exception as e:
        raise FileNotFoundError(f"Could not read audio file {audio_file}: {e}")

    # Ensure mono audio
    if audio_data.ndim > 1:
        if audio_data.shape[1] > 1:
            # Convert to mono by averaging channels
            audio_data = np.mean(audio_data, axis=1)
            print(f"Warning: Multi-channel audio converted to mono")

    # align sample_rate
    if not sample_rate == sr:
        audio_data = resampy.resample(audio_data, sr, sample_rate)

    # create an array of shape (n_bands,audio_length)
    n_bands = len(frequency_bands)
    audio_length = audio_data.shape[0]
    multi_bands_audio = np.zeros((n_bands,audio_length), dtype=np.float32)
    for index in range(n_bands):
        low_freq = frequency_bands[index][0]
        high_freq = frequency_bands[index][1]
        high_freq = high_freq if high_freq < sample_rate / 2 else (sample_rate / 2) - 1
        filtered_audio, sample_rate = LinkwitzRileyFilter.linkwitz_riley_bandpass_filter(audio_data, sample_rate, low_freq, high_freq)
        multi_bands_audio[index] = filtered_audio

    return multi_bands_audio
