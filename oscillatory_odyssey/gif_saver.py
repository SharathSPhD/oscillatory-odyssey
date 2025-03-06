"""GIF creation utilities for pendulum visualization."""

import os
import tempfile
import shutil
import numpy as np
import imageio
from IPython.display import display, Image
from plotly.io import to_image
import ipywidgets as widgets

def save_animation_as_gif(anim_fig, results, filename='pendulum_animation.gif', fps=30, quality=90, width=800, height=600):
    """Save animation as a GIF file.
    
    Args:
        anim_fig: Plotly figure widget for animation
        results: Simulation results dictionary
        filename: Output filename
        fps: Frames per second in the output GIF
        quality: Quality of the output GIF (0-100)
        width: Width of the output GIF in pixels
        height: Height of the output GIF in pixels
        
    Returns:
        widgets.HTML: HTML widget with status message and display of the GIF
    """
    try:
        # Create temporary directory for frames
        temp_dir = tempfile.mkdtemp()
        print(f"Saving animation as GIF to {filename}...")
        
        # Determine frame interval based on fps
        frame_interval = 1.0 / fps  # seconds per frame
        
        # Calculate required frames
        total_frames = len(results['t'])
        
        # We don't want too many frames for a reasonable GIF size
        # Calculate step to reduce number of frames if needed
        target_frames = min(100, total_frames)  # Max 100 frames for performance
        step = max(1, total_frames // target_frames)
        
        # Collect frame images
        frame_paths = []
        
        # Show progress
        progress = widgets.IntProgress(
            value=0,
            min=0,
            max=total_frames // step,
            description='Progress:',
            bar_style='info',
            orientation='horizontal'
        )
        display(progress)
        
        # Process frames
        for i in range(0, total_frames, step):
            # Create a copy of the animation figure
            fig_copy = anim_fig.to_dict()
            
            # Update rod
            fig_copy['data'][0]['x'] = [0, results['x'][i]]
            fig_copy['data'][0]['y'] = [0, results['y'][i]]
            # Update bob
            fig_copy['data'][1]['x'] = [results['x'][i]]
            fig_copy['data'][1]['y'] = [results['y'][i]]
            
            # Add time info to title
            time_str = results['t'][i].round(2)
            fig_copy['layout']['title']['text'] = f'Pendulum Animation (Time: {time_str}s)'
            
            # Convert to static image
            frame_path = os.path.join(temp_dir, f'frame_{i:04d}.png')
            image_bytes = to_image(fig_copy, format='png', width=width, height=height)
            
            with open(frame_path, 'wb') as f:
                f.write(image_bytes)
            
            frame_paths.append(frame_path)
            progress.value += 1
        
        # Combine frames into GIF
        frames = []
        for frame_path in frame_paths:
            frames.append(imageio.imread(frame_path))
        
        # Calculate duration of each frame in milliseconds
        duration = 1000 / fps  # milliseconds per frame
        
        # Create GIF
        imageio.mimsave(filename, frames, duration=duration, loop=0, quality=quality)
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        # Display the GIF
        gif = Image(filename=filename, format='gif')
        
        return widgets.HTML(
            f"Animation saved as GIF to <code>{filename}</code>.<br>"
            f"<div style='margin: 20px 0;'>{gif._repr_html_()}</div>"
        )
    
    except Exception as e:
        return widgets.HTML(f"Error saving animation as GIF: {str(e)}")
