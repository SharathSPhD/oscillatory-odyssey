"""Data handling and diagnostics for Hemispherical Resonator Gyroscope simulation."""

import os
import json
import datetime
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, HTML
import ipywidgets as widgets

def generate_statistics_html(results):
    """Generate HTML code for displaying simulation statistics.
    
    Args:
        results: Simulation results dictionary
        
    Returns:
        str: HTML code for statistics display
    """
    stats_html = f"""
    <div style="margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
        <h3>Simulation Statistics</h3>
        <table style="width: 100%;">
            <tr>
                <td style="width: 50%;"><b>Mean Error:</b> {results['mean_error']:.3e} rad/s</td>
                <td><b>Std Deviation:</b> {results['std_error']:.3e} rad/s</td>
            </tr>
            <tr>
                <td><b>Max Error:</b> {results['max_error']:.3e} rad/s</td>
                <td><b>Bryan Factor:</b> {results['bryan_factor']:.3f}</td>
            </tr>
            <tr>
                <td><b>Parametric Excitation:</b> {'Enabled' if results['parametric_excitation_enabled'] else 'Disabled'}</td>
                <td><b>Frequency Mismatch:</b> {results['frequency_mismatch']:.6f}</td>
            </tr>
        </table>
    </div>
    """
    return stats_html

def check_frequency_mismatch_warning(results):
    """Generate warning HTML if frequency mismatch may cause significant drift.
    
    Args:
        results: Simulation results dictionary
        
    Returns:
        str: HTML warning message or empty string if no warning needed
    """
    # Check if frequency mismatch is significant (above 0.001)
    if abs(results['frequency_mismatch']) > 0.001:
        warning_html = f"""
        <div style='background-color: #fff3cd; color: #856404; 
                 padding: 10px; border-radius: 5px; margin-top: 10px;'>
        <strong>Note:</strong> The current frequency mismatch ({results['frequency_mismatch']:.6f}) 
        is relatively high. This will cause significant pattern drift even without external rotation.
        This anisotropy effect is one of the primary error sources in real HRGs.
        </div>
        """
        return warning_html
    return ""

def save_diagnostics(results, simulation_path):
    """Save diagnostic information to files.
    
    Args:
        results: Simulation results dictionary
        simulation_path: Path to the main simulation module
        
    Returns:
        tuple: (success: bool, message: str, file_paths: list)
    """
    try:
        # Create diagnostics directory if it doesn't exist
        diag_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(simulation_path))), 
                               'notebooks', 'diagnostics')
        os.makedirs(diag_dir, exist_ok=True)
        
        # Create a timestamp for the filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"hrg_diagnostics_{timestamp}"
        
        # Collect file paths to return
        file_paths = []
        
        # Save parameters and results to JSON file
        diag_data = {
            "parameters": {
                "natural_frequency": results["natural_frequency"],
                "damping_ratio": results["damping_ratio"],
                "rotation_rate": results["rotation_rate"],
                "bryan_factor": results["bryan_factor"],
                "frequency_mismatch": results["frequency_mismatch"],
                "parametric_excitation_enabled": results["parametric_excitation_enabled"],
                "parametric_excitation_amp": results.get("parametric_excitation_amp", 0.0)
            },
            "statistics": {
                "mean_error": float(results.get('mean_error', 0)),
                "std_error": float(results.get('std_error', 0)),
                "max_error": float(results.get('max_error', 0))
            },
            "simulation_info": {
                "time_points": len(results['t']),
                "total_simulation_time": float(results['t'][-1]),
                "rotation_rate": float(results['rotation_rate']),
                "bryan_factor": float(results['bryan_factor']),
                "frequency_mismatch": float(results['frequency_mismatch']),
                "scale_factor": float(results.get('scale_factor', 0.0))
            }
        }
        
        # Write to JSON file
        json_path = os.path.join(diag_dir, f"{base_filename}.json")
        with open(json_path, 'w') as f:
            json.dump(diag_data, f, indent=2)
        file_paths.append(json_path)
            
        # Save key time series data to CSV for analysis
        csv_path = os.path.join(diag_dir, f"{base_filename}.csv")
        with open(csv_path, 'w') as f:
            # Write header
            f.write("time,x,y,phase,measured_rotation_rate,actual_rotation_rate,error\n")
            
            # Write data rows
            for i in range(len(results['t'])):
                f.write(f"{results['t'][i]},{results['x'][i]},{results['y'][i]},")
                f.write(f"{results['phase'][i]},{results['measured_rotation_rate'][i]},")
                f.write(f"{results['actual_rotation_rate'][i]},{results['error'][i]}\n")
        file_paths.append(csv_path)
        
        # Save diagnostic plots
        plt_path = os.path.join(diag_dir, f"{base_filename}_plots.png")
        save_diagnostic_plots(results, plt_path)
        file_paths.append(plt_path)
        
        return True, f"Diagnostic data saved successfully", file_paths
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return False, f"Error saving diagnostic data: {str(e)}\n{error_details}", []

def save_diagnostic_plots(results, filepath):
    """Save diagnostic plots to a file.
    
    Args:
        results: Simulation results dictionary
        filepath: Path where to save the plots
    """
    # Create a figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: X and Y displacements
    axs[0, 0].plot(results['t'], results['x'], 'b-', label='X Mode')
    axs[0, 0].plot(results['t'], results['y'], 'r-', label='Y Mode')
    axs[0, 0].set_xlabel('Time (s)')
    axs[0, 0].set_ylabel('Displacement')
    axs[0, 0].grid(True)
    axs[0, 0].legend()
    axs[0, 0].set_title('Mode Displacements')
    
    # Plot 2: Phase space
    axs[0, 1].plot(results['x'], results['y'], 'b-')
    axs[0, 1].set_xlabel('X Displacement')
    axs[0, 1].set_ylabel('Y Displacement')
    axs[0, 1].grid(True)
    axs[0, 1].set_aspect('equal')
    axs[0, 1].set_title('Phase Space Trajectory')
    
    # Plot 3: Phase angle
    axs[1, 0].plot(results['t'], results['phase_unwrapped'], 'purple')
    axs[1, 0].set_xlabel('Time (s)')
    axs[1, 0].set_ylabel('Phase (rad)')
    axs[1, 0].grid(True)
    axs[1, 0].set_title('Vibration Pattern Phase')
    
    # Plot 4: Rotation rates and error
    axs[1, 1].plot(results['t'], results['measured_rotation_rate'], 'b-', label='Measured')
    axs[1, 1].plot(results['t'], results['actual_rotation_rate'], 'g-', label='Actual')
    axs[1, 1].plot(results['t'], results['error'], 'r--', label='Error', alpha=0.5)
    axs[1, 1].set_xlabel('Time (s)')
    axs[1, 1].set_ylabel('Rotation Rate (rad/s)')
    axs[1, 1].grid(True)
    axs[1, 1].legend()
    axs[1, 1].set_title('Rotation Rate Measurement')
    
    # Add title with key parameters
    plt.suptitle(f"Hemispherical Resonator Gyro Diagnostics\n" 
               f"Rot. Rate: {results['rotation_rate']:.3f} rad/s, " 
               f"Bryan Factor: {results['bryan_factor']:.3f}, " 
               f"Freq. Mismatch: {results['frequency_mismatch']:.6f}")
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(filepath, dpi=150)
    plt.close(fig)

def update_gyro_display(hrg, controls):
    """Update the HRG information display with current parameters.
    
    Args:
        hrg: HemisphericalResonatorGyroSimulation instance
        controls: Dictionary of control widgets
    """
    # Update HRG parameters from controls
    hrg.params['rotation_rate'] = controls['rotation_rate'].value
    hrg.params['bryan_factor'] = controls['bryan_factor'].value
    
    # Update derived parameters
    hrg.update_derived_parameters()
    
    # Get values
    scale_factor = hrg.params['scale_factor']
    rotation_rate = controls['rotation_rate'].value
    bryan_factor = controls['bryan_factor'].value
    natural_frequency = hrg.params['natural_frequency']
    quality_factor = hrg.params['quality_factor']
    
    # Update display with formatted values
    controls['gyro_display'].value = (
        f"<b>Scale factor = {scale_factor:.3e} (rad/rad/s)</b><br>"
        f"Bryan factor = {bryan_factor:.3f}<br>"
        f"Natural frequency = {natural_frequency} Hz<br>"
        f"Quality factor = {quality_factor:.1f}"
    )
