"""
Sound Manager Class
Manages all sound effects and background music for the game.
"""

import pygame
import os
from typing import Optional


class SoundManager:
    """Sound effects and music manager for the 3D Gomoku game"""
    
    def __init__(self):
        """Initialize sound manager"""
        self.sounds = {}
        self.music_playing = False
        self.sound_enabled = True
        self.music_enabled = True
        self.volume = 0.7
        
        # Initialize pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Create default sounds
        self.create_default_sounds()
    
    def create_default_sounds(self):
        """Create default sound effects using pygame"""
        # Stone placement sound (beep)
        self.sounds['stone_place'] = self.create_beep_sound(800, 100)
        
        # Win sound (victory beep)
        self.sounds['win'] = self.create_beep_sound(1000, 300)
        
        # Invalid move sound (error beep)
        self.sounds['invalid'] = self.create_beep_sound(400, 200)
        
        # Button click sound
        self.sounds['click'] = self.create_beep_sound(600, 50)
        
        # Game start sound
        self.sounds['start'] = self.create_beep_sound(1200, 150)
    
    def create_beep_sound(self, frequency: int, duration: int) -> pygame.mixer.Sound:
        """
        Create a simple beep sound
        
        Args:
            frequency (int): Sound frequency in Hz
            duration (int): Duration in milliseconds
            
        Returns:
            pygame.mixer.Sound: Generated sound
        """
        # Generate a simple sine wave
        sample_rate = 44100
        samples = int(sample_rate * duration / 1000)
        
        # Create sine wave
        import math
        wave = []
        for i in range(samples):
            value = math.sin(2 * math.pi * frequency * i / sample_rate)
            wave.append(int(value * 32767))
        
        # Convert to bytes
        import array
        wave_array = array.array('h', wave)
        
        # Create sound
        sound = pygame.mixer.Sound(buffer=wave_array)
        sound.set_volume(self.volume)
        
        return sound
    
    def play_sound(self, sound_name: str):
        """
        Play a sound effect
        
        Args:
            sound_name (str): Name of the sound to play
        """
        if not self.sound_enabled:
            return
            
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_stone_place(self):
        """Play stone placement sound"""
        self.play_sound('stone_place')
    
    def play_win(self):
        """Play win sound"""
        self.play_sound('win')
    
    def play_invalid(self):
        """Play invalid move sound"""
        self.play_sound('invalid')
    
    def play_click(self):
        """Play button click sound"""
        self.play_sound('click')
    
    def play_start(self):
        """Play game start sound"""
        self.play_sound('start')
    
    def set_volume(self, volume: float):
        """
        Set sound volume
        
        Args:
            volume (float): Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        
        # Update all sounds
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
    
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        self.sound_enabled = not self.sound_enabled
    
    def toggle_music(self):
        """Toggle background music on/off"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled and self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
    
    def cleanup(self):
        """Clean up sound resources"""
        pygame.mixer.quit() 