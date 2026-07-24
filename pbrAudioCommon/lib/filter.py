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

from typing import Dict, List, Tuple, Optional, Union
import numpy as np
import numba as nb
import soundfile as sf
from scipy import signal

class LinkwitzRileyFilter:
    """Second-order Linkwitz-Riley IIR filter implementation"""
    
    def __init__(self, filter_type: str = "lowpass", cutoff_frequency: float = 1000.0,
                 sample_rate: int = 48000, order: int = 2, **kwargs):
        
        self.filter_type = filter_type.lower()
        self.cutoff_frequency = cutoff_frequency
        self.sample_rate = sample_rate
        self.order = order
        
        # Filter coefficients
        self.b_coeffs = np.array([])
        self.a_coeffs = np.array([])
        
        # Design the filter
        self._design_filter()
    
    def _design_filter(self):
        """Design Linkwitz-Riley filter coefficients"""
        nyquist = self.sample_rate / 2
        normalized_cutoff = self.cutoff_frequency / nyquist
        
        if self.filter_type == "lowpass":
            self.b_coeffs, self.a_coeffs = signal.butter(
                self.order, normalized_cutoff, btype='low', analog=False
            )
        elif self.filter_type == "highpass":
            self.b_coeffs, self.a_coeffs = signal.butter(
                self.order, normalized_cutoff, btype='high', analog=False
            )
        elif self.filter_type == "bandpass":
            if isinstance(self.cutoff_frequency, (list, tuple)) and len(self.cutoff_frequency) == 2:
                low_cutoff, high_cutoff = self.cutoff_frequency
                normalized_low = low_cutoff / nyquist
                normalized_high = high_cutoff / nyquist
                self.b_coeffs, self.a_coeffs = signal.butter(
                    self.order, [normalized_low, normalized_high], btype='band', analog=False
                )
            else:
                raise ValueError("Bandpass filter requires [low_freq, high_freq] for cutoff_frequency")
        elif self.filter_type == "bandstop":
            if isinstance(self.cutoff_frequency, (list, tuple)) and len(self.cutoff_frequency) == 2:
                low_cutoff, high_cutoff = self.cutoff_frequency
                normalized_low = low_cutoff / nyquist
                normalized_high = high_cutoff / nyquist
                self.b_coeffs, self.a_coeffs = signal.butter(
                    self.order, [normalized_low, normalized_high], btype='bandstop', analog=False
                )
            else:
                raise ValueError("Bandstop filter requires [low_freq, high_freq] for cutoff_frequency")
        elif self.filter_type == "allpass":
            self.b_coeffs, self.a_coeffs = signal.butter(
                self.order, normalized_cutoff, btype='low', analog=False
            )
            # Convert lowpass to allpass (simplified approach)
            # In practice, you'd use a proper allpass design
            self.b_coeffs = self.a_coeffs[::-1]  # Reverse coefficients for allpass
        else:
            raise ValueError(f"Unsupported filter type: {self.filter_type}")
    
    def apply_filter(self, audio_signal: np.ndarray, 
                    zi: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply filter to audio signal.
        
        Args:
            audio_signal: Input audio signal
            zi: Initial filter state (optional)
        
        Returns:
            (filtered_signal, final_filter_state)
        """
        if len(self.b_coeffs) == 0 or len(self.a_coeffs) == 0:
            return audio_signal, np.array([])
        
        if zi is None:
            # Calculate initial state
            zi = signal.lfilter_zi(self.b_coeffs, self.a_coeffs)
        
        filtered_signal, zf = signal.lfilter(self.b_coeffs, self.a_coeffs, audio_signal, zi=zi)
        
        return filtered_signal, zf
    
    def cascade_filters(self, other_filter: 'LinkwitzRileyFilter') -> 'LinkwitzRileyFilter':
        """Cascade this filter with another filter"""
        # Combine filter coefficients
        b_combined = np.convolve(self.b_coeffs, other_filter.b_coeffs)
        a_combined = np.convolve(self.a_coeffs, other_filter.a_coeffs)
        
        # Create new filter
        combined_filter = LinkwitzRileyFilter(
            filter_type=self.filter_type,  # This might need adjustment
            cutoff_frequency=self.cutoff_frequency,
            sample_rate=self.sample_rate,
            order=self.order + other_filter.order
        )
        
        combined_filter.b_coeffs = b_combined
        combined_filter.a_coeffs = a_combined
        
        return combined_filter
    
    def to_dict(self) -> Dict:
        """Convert filter to dictionary"""
        return {
            'filter_type': self.filter_type,
            'cutoff_frequency': self.cutoff_frequency,
            'sample_rate': self.sample_rate,
            'order': self.order,
            'b_coeffs': self.b_coeffs.tolist(),
            'a_coeffs': self.a_coeffs.tolist()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LinkwitzRileyFilter':
        """Create filter from dictionary"""
        filter_obj = cls(
            filter_type=data['filter_type'],
            cutoff_frequency=data['cutoff_frequency'],
            sample_rate=data['sample_rate'],
            order=data['order']
        )
        filter_obj.b_coeffs = np.array(data['b_coeffs'])
        filter_obj.a_coeffs = np.array(data['a_coeffs'])
        return filter_obj

    def linkwitz_riley_bandpass_filter(audio_data: np.ndarray, 
                                     sample_rate: int, 
                                     low_cutoff: float, 
                                     high_cutoff: float, 
                                     order: int = 2) -> Tuple[np.ndarray, int]:
        """
        Apply a Second-order Linkwitz-Riley bandpass filter to a mono PCM WAV in np.ndarray.
    
        Args:
            audio_data: np.ndarray of mono audio samples from soundfile
            sample_rate: Target sample rate (optional, uses file's sample rate if None)
            low_cutoff: Low cutoff frequency in Hz
            high_cutoff: High cutoff frequency in Hz
            order: Filter order (2 for second-order Linkwitz-Riley)
    
        Returns:
            Tuple of (filtered_audio, sample_rate)
    
        Raises:
            ValueError: If cutoff frequencies are invalid
        """
    
        # Validate cutoff frequencies
        nyquist = sample_rate / 2
        if low_cutoff >= high_cutoff:
            raise ValueError("Low cutoff frequency must be less than high cutoff frequency")
        if low_cutoff <= 0 or high_cutoff <= 0:
            raise ValueError("Cutoff frequencies must be positive")
        if high_cutoff >= nyquist:
            raise ValueError(f"High cutoff frequency must be less than Nyquist frequency ({nyquist:.1f} Hz)")
    
#        print(f"Filtering: {low_cutoff}-{high_cutoff} Hz bandpass at {sample_rate} Hz sample rate")
    
        # Create Linkwitz-Riley bandpass filter using cascaded lowpass and highpass
        # Linkwitz-Riley filters are Butterworth filters with specific cascade properties
    
        # Create lowpass filter (second order)
        lp_filter = LinkwitzRileyFilter(
        filter_type="lowpass",
            cutoff_frequency=high_cutoff,
            sample_rate=sample_rate,
            order=order
        )
    
        # Create highpass filter (second order)  
        hp_filter = LinkwitzRileyFilter(
            filter_type="highpass", 
            cutoff_frequency=low_cutoff,
            sample_rate=sample_rate,
            order=order
        )
    
        # Apply filters in cascade (highpass then lowpass for bandpass)
#        print("Applying highpass filter...")
        filtered_audio, zi_hp = hp_filter.apply_filter(audio_data)
    
#        print("Applying lowpass filter...")
        filtered_audio, zi_lp = lp_filter.apply_filter(filtered_audio)
    
        # Alternative: Use single bandpass filter (equivalent result for Linkwitz-Riley)
        # bandpass_filter = LinkwitzRileyFilter(
        #     filter_type="bandpass",
        #     cutoff_frequency=[low_cutoff, high_cutoff],
        #     sample_rate=sample_rate,
        #     order=order
        # )
        # filtered_audio, zi = bandpass_filter.apply_filter(audio_data)
    
        # Normalize to prevent clipping (optional)
        max_val = np.max(np.abs(filtered_audio))
        if max_val > 1.0:
            print(f"Normalizing output (peak: {max_val:.3f})")
            filtered_audio = filtered_audio / max_val * 0.99  # Leave some headroom
    
        # Write filtered audio to file
        #sf.write(output_file, filtered_audio, sample_rate)
        #print(f"Filtered audio saved to: {output_file}")
    
        return filtered_audio, sample_rate

    def linkwitz_riley_bandpass_filter_direct(audio_data: np.ndarray,
                                            sample_rate: int,
                                            low_cutoff: float,
                                            high_cutoff: float) -> Tuple[np.ndarray, int]:
        """
        Direct implementation using scipy.signal for Second-order Linkwitz-Riley bandpass.
    
        Linkwitz-Riley filters are specifically cascaded Butterworth filters where
        the -3dB points align perfectly when filters are summed.
        """

        nyquist = sample_rate / 2
    
        # Design 4th order Linkwitz-Riley bandpass as cascade of two 2nd-order Butterworth filters
        # This creates the characteristic flat summed response of Linkwitz-Riley filters
    
        # Highpass section (2nd order Butterworth)
        hp_b, hp_a = signal.butter(2, low_cutoff/nyquist, btype='high')
    
        # Lowpass section (2nd order Butterworth)  
        lp_b, lp_a = signal.butter(2, high_cutoff/nyquist, btype='low')
    
        # Apply highpass then lowpass (equivalent to bandpass)
        filtered_audio = signal.lfilter(hp_b, hp_a, audio_data)
        filtered_audio = signal.lfilter(lp_b, lp_a, filtered_audio)
    
        return filtered_audio, sample_rate

# Numba-accelerated filter functions
@nb.jit(nopython=True)
def apply_iir_filter_numba(signal: np.ndarray, b_coeffs: np.ndarray, 
                          a_coeffs: np.ndarray, zi: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply IIR filter using numba acceleration (direct form II transposed).
    
    Args:
        signal: Input signal
        b_coeffs: Numerator coefficients
        a_coeffs: Denominator coefficients
        zi: Initial filter state
    
    Returns:
        (filtered_signal, final_state)
    """
    if len(b_coeffs) == 0 or len(a_coeffs) == 0:
        return signal, np.zeros_like(zi)
    
    # Normalize coefficients if a[0] != 1
    if a_coeffs[0] != 1.0:
        b_coeffs = b_coeffs / a_coeffs[0]
        a_coeffs = a_coeffs / a_coeffs[0]
    
    filtered = np.zeros_like(signal)
    state = zi.copy()
    
    for n in range(len(signal)):
        # Direct Form II Transposed implementation
        filtered[n] = b_coeffs[0] * signal[n] + state[0]
        
        # Update state
        for i in range(1, len(state)):
            state[i-1] = b_coeffs[i] * signal[n] + state[i] - a_coeffs[i] * filtered[n]
        
        if len(state) > 0:
            state[-1] = b_coeffs[-1] * signal[n] - a_coeffs[-1] * filtered[n]
    
    return filtered, state
