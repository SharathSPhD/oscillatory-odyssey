"""Animation saving utilities for pendulum visualization."""

import os
import base64
import tempfile
import shutil
import ipywidgets as widgets
from IPython.display import HTML

def save_animation(anim_fig, plots_fig, results):
    """Save animation as HTML and return the HTML file content."""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, 'pendulum_animation.html')
        
        # Create standalone HTML with both figures and animation controls
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Parametric Pendulum Animation</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ display: flex; flex-direction: column; gap: 20px; }}
                h1 {{ color: #333366; }}
                .controls {{ margin: 15px 0; }}
                button {{ padding: 8px 15px; margin-right: 10px; cursor: pointer; background-color: #4CAF50; color: white; border: none; border-radius: 4px; }}
                button:hover {{ background-color: #45a049; }}
                #play {{ width: 80px; }}
            </style>
        </head>
        <body>
            <h1>Parametric Pendulum Animation</h1>
            <div class="container">
                <div class="controls">
                    <button id="play">Play</button>
                    <button id="reset">Reset</button>
                    <span id="time-display">Time: 0.00s</span>
                </div>
                <div id="animation-div" style="width:700px;height:500px;"></div>
                <div id="plots-div" style="width:1000px;height:800px;"></div>
            </div>
            <script>
                // Extract data needed for animation
                var times = {results['t'].tolist()};
                var theta = {results['theta'].tolist()};
                var omega = {results['omega'].tolist()};
                var xCoords = {results['x'].tolist()};
                var yCoords = {results['y'].tolist()};
                
                // Create plots using the original figure data
                var animData = {anim_fig.to_json()};
                var plotsData = {plots_fig.to_json()};
                
                // Create plots
                Plotly.newPlot('animation-div', animData.data, animData.layout, {{responsive: true}});
                Plotly.newPlot('plots-div', plotsData.data, plotsData.layout, {{responsive: true}});
                
                // Add time indicator shapes if they don't exist
                if (!plotsData.layout.shapes) {{
                    plotsData.layout.shapes = [];
                }}
                
                // Time indicator shapes (vertical lines at current time)
                // We need three shapes: one for angle plot, one for angular velocity plot, and one for energy plot
                // Shape for angle plot (xaxis)
                plotsData.layout.shapes.push({{
                    type: 'line',
                    x0: times[0],
                    x1: times[0],
                    y0: 0,
                    y1: 1,
                    yref: 'paper',
                    line: {{
                        color: 'red',
                        width: 2,
                        dash: 'dot'
                    }}
                }});
                
                // Shape for angular velocity plot (xaxis2)
                plotsData.layout.shapes.push({{
                    type: 'line',
                    x0: times[0],
                    x1: times[0],
                    y0: 0,
                    y1: 1,
                    yref: 'paper',
                    xref: 'x2',
                    line: {{
                        color: 'red',
                        width: 2,
                        dash: 'dot'
                    }}
                }});
                
                // Shape for energy plot (xaxis4)
                plotsData.layout.shapes.push({{
                    type: 'line',
                    x0: times[0],
                    x1: times[0],
                    y0: 0,
                    y1: 1,
                    yref: 'paper',
                    xref: 'x4',
                    line: {{
                        color: 'red',
                        width: 2,
                        dash: 'dot'
                    }}
                }});
                
                // Update plots with the shapes
                Plotly.relayout('plots-div', {{ shapes: plotsData.layout.shapes }});
                
                // Animation variables
                var currentFrame = 0;
                var animationId = null;
                var isPlaying = false;
                var fps = 30;
                var frameInterval = 1000 / fps;
                
                // Get DOM elements
                var playButton = document.getElementById('play');
                var resetButton = document.getElementById('reset');
                var timeDisplay = document.getElementById('time-display');
                
                // Find indices of specific traces
                var phaseMarkerIndex = -1;
                
                // Find the current state marker in the phase plot
                for (let i = 0; i < plotsData.data.length; i++) {{
                    if (plotsData.data[i].name === "Current State") {{
                        phaseMarkerIndex = i;
                        break;
                    }}
                }}
                
                // If current state marker doesn't exist, add it
                if (phaseMarkerIndex === -1) {{
                    // Find the phase plot trace
                    var phaseTraceIndex = -1;
                    for (let i = 0; i < plotsData.data.length; i++) {{
                        if (plotsData.data[i].name === "Phase") {{
                            phaseTraceIndex = i;
                            break;
                        }}
                    }}
                    
                    // Add the current state marker trace
                    Plotly.addTraces('plots-div', {{
                        x: [theta[0]],
                        y: [omega[0]],
                        mode: 'markers',
                        marker: {{
                            color: 'red',
                            size: 10,
                            symbol: 'star'
                        }},
                        name: 'Current State',
                        xaxis: plotsData.data[phaseTraceIndex].xaxis,
                        yaxis: plotsData.data[phaseTraceIndex].yaxis
                    }});
                    
                    // Update the phaseMarkerIndex
                    phaseMarkerIndex = plotsData.data.length;
                }}
                
                // Animation functions
                function updateFrame(frameIndex) {{
                    // Update pendulum position in animation
                    var pendulumUpdate = {{
                        'x': [[0, xCoords[frameIndex]], [xCoords[frameIndex]]],
                        'y': [[0, yCoords[frameIndex]], [yCoords[frameIndex]]]
                    }};
                    
                    Plotly.restyle('animation-div', pendulumUpdate, [0, 1]);
                    
                    // Update animation title and time display
                    var timeStr = times[frameIndex].toFixed(2);
                    timeDisplay.textContent = 'Time: ' + timeStr + 's';
                    Plotly.relayout('animation-div', {{ 
                        'title': 'Parametric Pendulum Animation (Time: ' + timeStr + 's)'
                    }});
                    
                    // Update phase plot current state marker
                    var markerUpdate = {{
                        x: [theta[frameIndex]],
                        y: [omega[frameIndex]]
                    }};
                    
                    Plotly.restyle('plots-div', markerUpdate, [phaseMarkerIndex]);
                    
                    // Update time indicator positions
                    var shapes = [
                        // Angle plot time indicator
                        {{
                            type: 'line',
                            x0: times[frameIndex],
                            x1: times[frameIndex],
                            y0: 0,
                            y1: 1,
                            yref: 'paper',
                            line: {{
                                color: 'red',
                                width: 2,
                                dash: 'dot'
                            }}
                        }},
                        // Angular velocity plot time indicator
                        {{
                            type: 'line',
                            x0: times[frameIndex],
                            x1: times[frameIndex],
                            y0: 0,
                            y1: 1,
                            yref: 'paper',
                            xref: 'x2',
                            line: {{
                                color: 'red',
                                width: 2,
                                dash: 'dot'
                            }}
                        }},
                        // Energy plot time indicator
                        {{
                            type: 'line',
                            x0: times[frameIndex],
                            x1: times[frameIndex],
                            y0: 0,
                            y1: 1,
                            yref: 'paper',
                            xref: 'x4',
                            line: {{
                                color: 'red',
                                width: 2,
                                dash: 'dot'
                            }}
                        }}
                    ];
                    
                    Plotly.relayout('plots-div', {{ shapes: shapes }});
                }}
                
                function nextFrame() {{                    
                    if (isPlaying) {{                        
                        currentFrame = (currentFrame + 1) % times.length;
                        updateFrame(currentFrame);
                        animationId = setTimeout(nextFrame, frameInterval);
                    }}
                }}
                
                function togglePlay() {{                    
                    isPlaying = !isPlaying;
                    
                    if (isPlaying) {{                        
                        playButton.textContent = 'Pause';
                        nextFrame();
                    }} else {{                        
                        playButton.textContent = 'Play';
                        clearTimeout(animationId);
                    }}
                }}
                
                function resetAnimation() {{                    
                    // Stop if playing
                    if (isPlaying) {{                        
                        togglePlay();
                    }}
                    
                    // Reset to first frame
                    currentFrame = 0;
                    updateFrame(0);
                }}
                
                // Set up event listeners
                playButton.addEventListener('click', togglePlay);
                resetButton.addEventListener('click', resetAnimation);
                
                // Initialize with first frame
                updateFrame(0);
            </script>
        </body>
        </html>
        """
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Read file for download link
        with open(output_file, 'rb') as f:
            html_data = f.read()
        
        # Create download link
        b64_html = base64.b64encode(html_data).decode()
        download_link = f'<a href="data:text/html;base64,{b64_html}" download="pendulum_animation.html">Download HTML Animation</a>'
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        return widgets.HTML(f"Animation saved as HTML.<br>{download_link}")
    
    except Exception as e:
        return widgets.HTML(f"Error saving animation: {str(e)}")
