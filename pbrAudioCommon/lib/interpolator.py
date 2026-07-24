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

import numpy as np
from typing import Union, List, Tuple, Optional, Dict, Any
from scipy import interpolate

class FrequencyInterpolator:
    """
    A class to interpolate values between frequency points within specified frequency bands.
    """
    
#    def __init__(self, frequencies: List[float], values: List[float], method: str = 'linear', extrapolate: bool = True):
    def __init__(self, frequencies: np.ndarray, values: np.ndarray, method: str = 'linear', extrapolate: bool = True):
        """
        Initialize the interpolator with frequency-value pairs.
        
        Args:
            frequencies: List of frequency points (must be strictly increasing)
            values: List of corresponding values at each frequency
            method: Interpolation method ('linear', 'cubic', 'nearest')
            extrapolate: Whether to extrapolate beyond the input frequency range
        """
#        if len(frequencies) != len(values):
        if frequencies.shape[0] != values.shape[0]:
            raise ValueError("Frequencies and values must have the same length")
        
#        if len(frequencies) < 2:
        if frequencies.shape[0] < 2:
            raise ValueError("At least 2 frequency-value pairs are required")
        
#        if not all(frequencies[i] < frequencies[i+1] for i in range(len(frequencies)-1)):
        if not all(frequencies[i] < frequencies[i+1] for i in range(frequencies.shape[0] - 1)):
            raise ValueError("Frequencies must be strictly increasing")
        
#        self.frequencies = np.array(frequencies)
#        self.values = np.array(values)
        self.frequencies = frequencies
        self.values = values
        self.method = method
        self.extrapolate = extrapolate
        
        # Create interpolation function
        self._setup_interpolator()
    
    def _setup_interpolator(self):
        """Set up the interpolation function based on the chosen method."""
        from scipy import interpolate
        
        if self.method == 'linear':
            self.interp_func = interpolate.interp1d(
                self.frequencies, self.values, 
                kind='linear',
                bounds_error=not self.extrapolate,
                fill_value='extrapolate' if self.extrapolate else np.nan
            )
        elif self.method == 'cubic':
            self.interp_func = interpolate.interp1d(self.frequencies, self.values, kind='cubic', bounds_error=not self.extrapolate, fill_value='extrapolate' if self.extrapolate else np.nan)
        elif self.method == 'nearest':
            self.interp_func = interpolate.interp1d(
                self.frequencies, self.values, 
                kind='nearest',
                bounds_error=not self.extrapolate,
                fill_value='extrapolate' if self.extrapolate else np.nan
            )
        else:
            raise ValueError("Method must be 'linear', 'cubic', or 'nearest'")
    
    def interpolate_band(self, low_freq: float, high_freq: float, 
                        num_points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Interpolate values within a frequency band.
        
        Args:
            low_freq: Lower frequency bound of the band
            high_freq: Upper frequency bound of the band
            num_points: Number of points to generate within the band
            
        Returns:
            Tuple of (frequencies, values) arrays within the specified band
        """
        if low_freq >= high_freq:
            raise ValueError("low_freq must be less than high_freq")
        
        # Generate frequency points within the band
        band_frequencies = np.linspace(low_freq, high_freq, num_points)
        
        # Interpolate values at these frequencies
        band_values = self.interp_func(band_frequencies)
        
        return band_frequencies, band_values
    
    def get_band_average(self, low_freq: float, high_freq: float, 
                        num_points: int = 1000) -> float:
        """
        Calculate the average value within a frequency band.
        
        Args:
            low_freq: Lower frequency bound of the band
            high_freq: Upper frequency bound of the band
            num_points: Number of points to use for averaging
            
        Returns:
            Average value within the specified band
        """
        _, values = self.interpolate_band(low_freq, high_freq, num_points)
        return float(np.mean(values))

class Frequency3DInterpolator:
    """
    A 3D interpolator for frequency data across azimuth and elevation dimensions.
    Handles nested arrays of frequency values organized by elevation and azimuth.
    """
    
    def __init__(self, 
                 azimuths: List[float],
                 elevations: List[float],
                 frequency_data: List[float],
                 value_data: List[List[List[float]]],
                 freq_method: str = 'linear',
                 spatial_method: str = 'linear',
                 extrapolate: bool = True):
        """
        Initialize the 3D interpolator.
        
        Args:
            azimuths: List of azimuth angles (degrees)
            elevations: List of elevation angles (degrees)
            frequency_data: List of frequencies (Hertz)
            value_data: Nested array of list of values [[[value],[value]],[[value],[value]]]
            freq_method: Frequency interpolation method ('linear', 'cubic', 'nearest')
            spatial_method: Spatial interpolation method ('linear', 'cubic')
            extrapolate: Whether to extrapolate beyond input ranges
        """
        self.azimuths = np.array(azimuths)
        self.elevations = np.array(elevations)
        self.frequency_data = np.array(frequency_data)
        self.value_data = np.array(value_data)
        self.freq_method = freq_method
        self.spatial_method = spatial_method
        self.extrapolate = extrapolate
        
        # Validate input dimensions
        self._validate_inputs()
        
        # Create frequency interpolators for each (azimuth, elevation) pair
        self._setup_frequency_interpolators()
        
        # Create spatial interpolation grid
        self._setup_spatial_interpolator()
    
    def _validate_inputs(self):
        """Validate input dimensions and consistency."""
        # Check that frequencies are strictly increasing)
        for i, freq_item in enumerate(self.frequency_data):
            if not all(self.frequency_data[k] < self.frequency_data[k+1] for k in range(len(self.frequency_data)-1)):
                raise ValueError(f"Frequencies must be strictly increasing")
    
        # Check that all value array length are equals
        if len(self.value_data) > 1:
            for index in range(len(self.value_data)-1):
                if len(self.value_data[index]) != len(self.value_data[index+1]):
                    raise ValueError("Value array length mismatch")

        # Check that value array length are equals to Frequency array length
        if len(self.frequency_data) != len(self.value_data[0][0]):
            raise ValueError(f"Frequency {len(self.frequency_data)} and value {len(self.value_data[0][0])} array length mismatch")

        # Check that the value_data array length is equals to azimuths for elevations
        ae = len(self.azimuths) * len(self.elevations)
        vd = len(self.value_data) * len(self.value_data[0])
        if vd != ae:
            raise ValueError(f"Number of value array {vd} must match number of azimuths for elevations {ae}")
        
    def _setup_frequency_interpolators(self):
        """Create FrequencyInterpolator instances for each (azimuth, elevation) pair."""
        self.freq_interpolators = []
        
        for i, az_data in enumerate(self.azimuths):
            elev_interpolators = []
            for j, el_data in enumerate(self.elevations):
                # Create FrequencyInterpolator for this (azimuth, elevation) pair
                interpolator = FrequencyInterpolator(
                    frequencies=self.frequency_data,
                    values=self.value_data[i][j],
                    method=self.freq_method,
                    extrapolate=self.extrapolate
                )
                elev_interpolators.append(interpolator)
            self.freq_interpolators.append(elev_interpolators)
    
    def _setup_spatial_interpolator(self):
        """Set up spatial interpolation grid for azimuth and elevation."""
        # Create meshgrid for spatial coordinates
        self.az_grid, self.el_grid = np.meshgrid(self.azimuths, self.elevations, indexing='ij')
        
        # We'll create interpolation functions on-demand for specific frequencies
        # to avoid creating a massive 4D interpolation function
    
    def _get_spatial_interpolation(self, target_frequency: float) -> interpolate.RegularGridInterpolator:
        """
        Create spatial interpolator for a specific frequency.
        
        Args:
            target_frequency: Frequency to create spatial interpolation for
            
        Returns:
            RegularGridInterpolator for spatial interpolation at target frequency
        """
        # Create value grid for this frequency
        value_grid = np.zeros((len(self.azimuths), len(self.elevations)))
        
        for i, az in enumerate(self.azimuths):
            for j, el in enumerate(self.elevations):
                # Get interpolated value at target frequency for this (azimuth, elevation)
                value_grid[i, j] = self.freq_interpolators[i][j].interpolate_at_frequency(target_frequency)
        
        # Create spatial interpolator
        return interpolate.RegularGridInterpolator(
            (self.azimuths, self.elevations),
            value_grid,
            method=self.spatial_method,
            bounds_error=not self.extrapolate,
            fill_value=np.nan if not self.extrapolate else None
        )
    
    def interpolate_at_point(self, 
                           azimuth: float, 
                           elevation: float, 
                           frequency: float) -> float:
        """
        Get interpolated value at specific azimuth, elevation, and frequency.
        
        Args:
            azimuth: Target azimuth angle (degrees)
            elevation: Target elevation angle (degrees)
            frequency: Target frequency
            
        Returns:
            Interpolated value at specified point
        """
        # First, create spatial interpolation for this frequency
        spatial_interp = self._get_spatial_interpolation(frequency)
        
        # Interpolate spatially
        return float(spatial_interp([[azimuth, elevation]])[0])
    
    def interpolate_band_at_point(self,
                                azimuth: float,
                                elevation: float,
                                low_freq: float,
                                high_freq: float,
                                num_points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Interpolate frequency band at specific azimuth and elevation.
        
        Args:
            azimuth: Target azimuth angle (degrees)
            elevation: Target elevation angle (degrees)
            low_freq: Lower frequency bound
            high_freq: Upper frequency bound
            num_points: Number of frequency points in band
            
        Returns:
            Tuple of (frequencies, values) arrays
        """
        # Find closest available (azimuth, elevation) for frequency interpolation
        az_idx = np.argmin(np.abs(self.azimuths - azimuth))
        el_idx = np.argmin(np.abs(self.elevations - elevation))
        
        # Use frequency interpolator at closest spatial point
        freq_interp = self.freq_interpolators[az_idx][el_idx]
        return freq_interp.interpolate_band(low_freq, high_freq, num_points)

    def get_band_average_at_point(self,
                                azimuth: float,
                                elevation: float,
                                low_freq: float,
                                high_freq: float,
                                num_points: int = 100) -> float:
        """
        Calculate the average value within a frequency band at specific azimuth and elevation.

        Args:
            azimuth: Target azimuth angle (degrees)
            elevation: Target elevation angle (degrees)
            low_freq: Lower frequency bound
            high_freq: Upper frequency bound
            num_points: Number of frequency points in band

        Returns:
            Average value within the specified band at specific azimuth and elevation
        """

        _, values = self.interpolate_band_at_point(azimuth, elevation, low_freq, high_freq, num_points)
        return float(np.mean(values))
    
    def interpolate_band_spatial_average(self,
                                       low_freq: float,
                                       high_freq: float,
                                       num_freq_points: int = 100,
                                       num_spatial_points: int = 10) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate spatial average across frequency band.
        
        Args:
            low_freq: Lower frequency bound
            high_freq: Upper frequency bound
            num_freq_points: Number of frequency points
            num_spatial_points: Number of spatial sample points per dimension
            
        Returns:
            Tuple of (frequencies, average_values, std_values) arrays
        """
        # Generate frequency points
        frequencies = np.linspace(low_freq, high_freq, num_freq_points)
        
        # Generate spatial sample points
        az_samples = np.linspace(self.azimuths.min(), self.azimuths.max(), num_spatial_points)
        el_samples = np.linspace(self.elevations.min(), self.elevations.max(), num_spatial_points)
        
        avg_values = []
        std_values = []
        
        for freq in frequencies:
            spatial_inter_interp = self._get_spatial_interpolation(freq)
            
            # Sample at all spatial points
            az_grid, el_grid = np.meshgrid(az_samples, el_samples)
            points = np.column_stack([az_grid.ravel(), el_grid.ravel()])
            sampled_values = spatial_interp(points)
            
            avg_values.append(np.nanmean(sampled_values))
            std_values.append(np.nanstd(sampled_values))
        
        return frequencies, np.array(avg_values), np.array(std_values)
