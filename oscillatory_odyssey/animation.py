"""Animation control and management for pendulum visualization."""

import threading
import time

class AnimationController:
    """Controls the animation loop and state."""
    
    def __init__(self, update_func):
        """Initialize animation controller.
        
        Args:
            update_func: Function to call for each animation frame
        """
        self.running = False
        self.current_frame = 0
        self.base_interval = 50  # base animation interval in milliseconds
        self.frame_interval = self.base_interval
        self.update_func = update_func
        self.animation_thread = None
        self.speed = 1.0
        
    def animation_loop(self, total_frames):
        """Main animation loop.
        
        Args:
            total_frames: Total number of frames in animation
        """
        while self.running:
            # Update frame
            self.current_frame = (self.current_frame + 1) % total_frames
            self.update_func(self.current_frame)
            
            # Control speed
            time.sleep(self.frame_interval / 1000 / self.speed)
            
    def start(self, total_frames):
        """Start the animation.
        
        Args:
            total_frames: Total number of frames in animation
        """
        if not self.running:
            self.running = True
            self.animation_thread = threading.Thread(
                target=self.animation_loop,
                args=(total_frames,)
            )
            self.animation_thread.daemon = True
            self.animation_thread.start()
            
    def stop(self):
        """Stop the animation."""
        self.running = False
        if self.animation_thread:
            self.animation_thread.join(timeout=0.1)
            
    def reset(self):
        """Reset animation to first frame."""
        self.stop()
        self.current_frame = 0
        self.update_func(0)
        
    def set_speed(self, speed):
        """Set animation speed multiplier.
        
        Args:
            speed: Speed multiplier (1.0 = normal speed)
        """
        self.speed = speed