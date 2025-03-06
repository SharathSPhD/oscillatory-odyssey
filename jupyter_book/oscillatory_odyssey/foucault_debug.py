"""
Debug utilities for the Foucault pendulum simulations.
"""

import os
import time
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def save_debug_information(pendulum, results, folder='debug_output'):
    """
    Save debug information to diagnose precession rate calculation issues.
    
    Parameters:
    -----------
    pendulum : FoucaultPendulum
        The pendulum instance with parameters
    results : dict
        Simulation results dictionary
    folder : str, optional
        Output folder path
        
    Returns:
    --------
    str
        Status message
    """
    try:
        # Create output folder if needed
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        # Create timestamp for filenames
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save parameters
        params_file = os.path.join(folder, f"params_{timestamp}.json")
        with open(params_file, 'w') as f:
            json.dump(pendulum.params, f, indent=4)
        
        # Save numerical results focused on precession data
        data_dict = {
            "time": results["t"],
            "theta": results["theta"],
            "phi": results["phi"],
            "phi_unwrapped": results["phi_unwrapped"],
            "omega": results["omega"]
        }
        df = pd.DataFrame(data_dict)
        csv_file = os.path.join(folder, f"precession_data_{timestamp}.csv")
        df.to_csv(csv_file, index=False)
        
        # Create and save analysis file
        analysis_file = os.path.join(folder, f"precession_analysis_{timestamp}.txt")
        with open(analysis_file, 'w') as f:
            f.write("FOUCAULT PENDULUM PRECESSION ANALYSIS\n")
            f.write("===================================\n\n")
            
            # Parameter summary
            f.write("SIMULATION PARAMETERS:\n")
            f.write(f"  Latitude: {pendulum.params['latitude']} degrees\n")
            f.write(f"  Rotation rate: {pendulum.params['rotation_rate']} rad/s\n")
            f.write(f"  Demo factor: {pendulum.params['rotation_demo_factor']}\n")
            
            # Theoretical calculations
            f.write("\nTHEORETICAL CALCULATIONS:\n")
            latitude_rad = np.radians(pendulum.params["latitude"])
            earth_rate = pendulum.params["rotation_rate"]
            f.write(f"  Earth rotation rate: {earth_rate} rad/s\n")
            f.write(f"  sin(latitude): {np.sin(latitude_rad)}\n")
            theoretical_rate_rad = earth_rate * np.sin(latitude_rad)
            theoretical_rate_deg = theoretical_rate_rad * 180 / np.pi
            f.write(f"  Theoretical precession rate: {theoretical_rate_rad} rad/s = {theoretical_rate_deg} deg/s\n")
            
            # Measured precession
            f.write("\nMEASURED PRECESSION:\n")
            if "regression_r_value" in results:
                f.write(f"  Regression R value: {results['regression_r_value']}\n")
                f.write(f"  Regression R^2: {results['regression_r_value']**2}\n")
            
            if "measured_precession_rate" in results:
                measured_rate = results["measured_precession_rate"]
                expected_rate = results["theoretical_precession_rate"]
                f.write(f"  Measured rate: {measured_rate} deg/s\n")
                f.write(f"  Expected rate: {expected_rate} deg/s\n")
                
                if "precession_error_percent" in results:
                    error = results["precession_error_percent"]
                    f.write(f"  Error percentage: {error}%\n")
            
            # Raw data analysis
            phi_start = results["phi_unwrapped"][0]
            phi_end = results["phi_unwrapped"][-1]
            total_change_rad = phi_end - phi_start
            total_change_deg = total_change_rad * 180 / np.pi
            total_time = results["t"][-1] - results["t"][0]
            avg_rate_rad = total_change_rad / total_time
            avg_rate_deg = avg_rate_rad * 180 / np.pi
            
            f.write("\nRAW DATA ANALYSIS:\n")
            f.write(f"  Initial phi: {phi_start} rad\n")
            f.write(f"  Final phi: {phi_end} rad\n")
            f.write(f"  Total change: {total_change_rad} rad = {total_change_deg} deg\n")
            f.write(f"  Total time: {total_time} s\n")
            f.write(f"  Average rate: {avg_rate_rad} rad/s = {avg_rate_deg} deg/s\n")
            
            # Debug info from precession calculation
            if "precession_debug" in results:
                debug = results["precession_debug"]
                f.write("\nDETAILED DEBUG INFO:\n")
                for key, value in debug.items():
                    f.write(f"  {key}: {value}\n")
        
        # Create a simple diagnostic plot
        plt.figure(figsize=(10, 6))
        plt.plot(results["t"], results["phi_unwrapped"] * 180 / np.pi, 'b-', label="phi_unwrapped")
        
        if "measured_precession_rate" in results:
            # Add regression line
            t = results["t"]
            regression_line = t * results["measured_precession_rate"] * np.pi / 180 + results["phi_unwrapped"][0]
            plt.plot(t, regression_line * 180 / np.pi, 'r--', label="Measured rate")
            
            # Add expected line
            expected_line = t * results["theoretical_precession_rate"] * np.pi / 180 + results["phi_unwrapped"][0]
            plt.plot(t, expected_line * 180 / np.pi, 'g--', label="Expected rate")
        
        plt.xlabel("Time (s)")
        plt.ylabel("Direction (deg)")
        plt.title("Precession Analysis")
        plt.legend()
        plt.grid(True)
        
        plot_file = os.path.join(folder, f"precession_plot_{timestamp}.png")
        plt.savefig(plot_file, dpi=150)
        plt.close()
        
        # Also create omega vs theta plot
        plt.figure(figsize=(8, 8))
        plt.plot(results["theta"], results["omega"])
        plt.xlabel("Angle θ (rad)")
        plt.ylabel("Angular Velocity ω (rad/s)")
        plt.title("Angular Velocity vs Angle (Phase Space)")
        plt.grid(True)
        plt.axis('equal')
        
        phase_plot_file = os.path.join(folder, f"phase_space_{timestamp}.png")
        plt.savefig(phase_plot_file, dpi=150)
        plt.close()
        
        return f"Debug info saved to '{folder}' folder with timestamp {timestamp}"
        
    except Exception as e:
        return f"Error saving debug info: {str(e)}"
