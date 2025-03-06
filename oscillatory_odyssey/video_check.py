"""Utility to check ffmpeg and video codec availability for video saving."""

import os
import sys
import subprocess
import platform

def check_ffmpeg_installation():
    """Check if ffmpeg is installed and available, and which video codecs are supported.
    
    Returns:
        dict: Dictionary with information about ffmpeg availability and codecs
    """
    result = {
        "ffmpeg_found": False,
        "ffmpeg_path": None,
        "system_ffmpeg_path": None,
        "libx264_available": False,
        "available_codecs": [],
        "error": None,
        "version": None,
        "detailed_info": None
    }
    
    # First check for system ffmpeg installation
    system_ffmpeg_paths = [
        "C:\\ffmpeg\\bin\\ffmpeg.exe",  # Common Windows location
        "/usr/bin/ffmpeg",             # Common Linux location
        "/usr/local/bin/ffmpeg"        # Common macOS location
    ]
    
    for path in system_ffmpeg_paths:
        if os.path.exists(path):
            result["system_ffmpeg_path"] = path
            break
    
    try:
        # Try to import imageio_ffmpeg and get ffmpeg path
        import imageio_ffmpeg
        
        # If system ffmpeg is found, set environment variable
        if result["system_ffmpeg_path"]:
            os.environ["IMAGEIO_FFMPEG_EXE"] = result["system_ffmpeg_path"]
            ffmpeg_path = result["system_ffmpeg_path"]
        else:
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            
        result["ffmpeg_found"] = True
        result["ffmpeg_path"] = ffmpeg_path
        
        # Check ffmpeg version
        try:
            version_output = subprocess.check_output([ffmpeg_path, "-version"], 
                                                    stderr=subprocess.STDOUT,
                                                    universal_newlines=True)
            result["version"] = version_output.splitlines()[0]
            result["detailed_info"] = version_output
        except Exception as e:
            result["error"] = f"Error getting ffmpeg version: {str(e)}"
        
        # Check available codecs - first check with -encoders (more reliable for encoding)
        try:
            encoders_output = subprocess.check_output([ffmpeg_path, "-encoders"], 
                                                    stderr=subprocess.STDOUT,
                                                    universal_newlines=True)
            
            # Debug: Save the full output for reference
            result["encoders_output"] = encoders_output
            
            # First check the configuration, which is more reliable
            if "--enable-libx264" in encoders_output or "enable-libx264" in encoders_output:
                result["libx264_available"] = True
                result["available_codecs"].append("libx264")
                print("Detected libx264 support in ffmpeg build configuration")
            
            # Also look for h264/libx264 in the encoders list
            codec_found = False
            for line in encoders_output.splitlines():
                # Check for any of these patterns that indicate h264 encoding capability
                h264_patterns = ["libx264", "h264", "h.264", "mpeg4 avc"]
                
                # More lenient detection - just look for video encoder lines with our patterns
                is_video_line = "V" in line[:10]  # Video encoder lines start with V
                
                if is_video_line and any(pattern in line.lower() for pattern in h264_patterns):
                    result["libx264_available"] = True
                    codec_name = line.split()[1] if len(line.split()) > 1 else "h264"
                    if codec_name not in result["available_codecs"]:
                        result["available_codecs"].append(codec_name)
                    codec_found = True
                    
                # Also detect other common video codecs
                if is_video_line:
                    codec_name = line.split()[1] if len(line.split()) > 1 else ""
                    if codec_name and codec_name not in result["available_codecs"]:
                        if any(name in line.lower() for name in ["mpeg4", "libvpx", "theora", "webm", "vp8", "vp9"]):
                            result["available_codecs"].append(codec_name)
            
            # If we didn't find h264 with encoders, also try checking -codecs as backup
            if not codec_found:
                codecs_output = subprocess.check_output([ffmpeg_path, "-codecs"], 
                                                      stderr=subprocess.STDOUT,
                                                      universal_newlines=True)
                
                for line in codecs_output.splitlines():
                    if ("libx264" in line or "h264" in line) and " E " in line:  # Encoding codec
                        result["libx264_available"] = True
                        result["available_codecs"].append("libx264")
                    elif "mpeg4" in line and " E " in line:
                        result["available_codecs"].append("mpeg4")
                    elif "libvpx" in line and " E " in line:
                        result["available_codecs"].append("libvpx")
                    elif "libtheora" in line and " E " in line:
                        result["available_codecs"].append("libtheora")
        except Exception as e:
            result["error"] = f"Error checking ffmpeg codecs: {str(e)}"
            
    except ImportError:
        result["error"] = "imageio_ffmpeg is not installed"
    except Exception as e:
        result["error"] = f"Error checking ffmpeg: {str(e)}"
    
    return result

def print_check_results(check_results):
    """Print the ffmpeg check results in a readable format.
    
    Args:
        check_results: Dictionary with check results
    """
    print("=" * 50)
    print("FFMPEG VIDEO CAPABILITY CHECK")
    print("=" * 50)
    
    # Print basic ffmpeg info
    if check_results["ffmpeg_found"]:
        print(f"✓ FFMPEG found at: {check_results['ffmpeg_path']}")
        if check_results["system_ffmpeg_path"]:
            print(f"  Using system installation (preferred for more codecs)")
        if check_results["version"]:
            print(f"  Version: {check_results['version']}")
    else:
        print("✗ FFMPEG not found")
        print(f"  Error: {check_results['error']}")
        print("\
Please install ffmpeg. On most systems, you can install it with:")
        if platform.system() == "Windows":
            print("  1. Download from https://ffmpeg.org/download.html")
            print("  2. Add ffmpeg bin directory to your PATH environment variable")
        elif platform.system() == "Darwin":  # macOS
            print("  brew install ffmpeg")
        else:  # Linux
            print("  apt-get install ffmpeg  # Debian/Ubuntu")
            print("  or")
            print("  yum install ffmpeg      # CentOS/RHEL")
        print("\
Alternatively, you can install ffmpeg via conda:")
        print("  conda install -c conda-forge ffmpeg")
        print("=" * 50)
        return
    
    # Print codec info
    if check_results["libx264_available"]:
        print("✓ libx264 codec available (best quality for MP4)")
    else:
        print("✗ libx264 codec NOT available (required for best quality MP4)")
        
    print(f"\
Available video codecs: {', '.join(check_results['available_codecs'])}")
    
    # Show raw encoder output for debugging if libx264 was not detected
    if not check_results["libx264_available"] and "encoders_output" in check_results:
        print("\nFFmpeg encoders output (for debugging):\n" + "-"*40)
        print(check_results["encoders_output"])
        print("-"*40)
    
    # Print recommendation
    if not check_results["libx264_available"]:
        print("\
Recommendation:")
        print("  To use the save video feature with H.264/MP4, install ffmpeg with libx264 support.")
        print("  On most systems, the standard ffmpeg installation includes libx264.")
        if platform.system() == "Windows":
            print("  For Windows, download the full build from https://ffmpeg.org/download.html")
        elif platform.system() == "Darwin":  # macOS
            print("  For macOS: brew install ffmpeg")
        else:  # Linux
            print("  For Ubuntu/Debian: apt-get install ffmpeg libx264-dev")
            print("  For CentOS/RHEL: yum install ffmpeg x264-devel")
    
    # Overall status
    print("\
Status:")
    if check_results["ffmpeg_found"] and len(check_results["available_codecs"]) > 0:
        if check_results["libx264_available"]:
            print("✓ System is fully capable of saving high-quality MP4 videos")
        else:
            print("! System can save videos, but without H.264 codec (quality may be lower)")
    else:
        print("✗ System cannot save videos (no encoding codecs available)")
    
    print("=" * 50)

def run_check():
    """Run the ffmpeg check and print results."""
    check_results = check_ffmpeg_installation()
    print_check_results(check_results)
    return check_results

if __name__ == "__main__":
    run_check()
