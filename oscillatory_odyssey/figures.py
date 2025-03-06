"""Figure creation and management for pendulum visualization."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_animation_figure(results):
    """Create Plotly figure for pendulum animation."""
    fig = go.FigureWidget()
    
    # Add pendulum rod trace
    fig.add_trace(
        go.Scatter(
            x=[0, results['x'][0]], 
            y=[0, results['y'][0]],
            mode='lines',
            line=dict(color='gray', width=2),
            name='Rod'
        )
    )
    
    # Add pendulum bob trace
    fig.add_trace(
        go.Scatter(
            x=[results['x'][0]],
            y=[results['y'][0]],
            mode='markers',
            marker=dict(size=15, color='red'),
            name='Bob'
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Pendulum Animation',
        height=400,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='white',
        hovermode='closest'
    )
    
    # Update axes
    fig.update_xaxes(
        range=[-3, 3],
        title='x (m)',
        showgrid=True,
        gridcolor='lightgray'
    )
    
    fig.update_yaxes(
        range=[-3, 3],
        title='y (m)',
        scaleanchor="x",
        scaleratio=1,
        showgrid=True,
        gridcolor='lightgray'
    )
    
    return fig

def create_plots_figure(results):
    """Create Plotly figure for time series plots."""
    fig = go.FigureWidget(make_subplots(rows=2, cols=2,
                       subplot_titles=('Angle vs Time', 'Phase Plot',
                                     'Angular Velocity vs Time', 'Energy')))
    
    t = results['t']
    
    # Add angle plot
    fig.add_trace(
        go.Scatter(x=t, y=results['theta'],
                  name='Angle', line=dict(color='blue', dash='solid'),
                  showlegend=False),
        row=1, col=1
    )
    
    # Add phase plot and current state marker
    fig.add_trace(
        go.Scatter(x=results['theta'], y=results['omega'],
                  name='Phase', mode='lines',
                  line=dict(color='purple', width=2),
                  showlegend=False),
        row=1, col=2
    )
    
    # Current state marker on phase plot
    fig.add_trace(
        go.Scatter(x=[results['theta'][0]], y=[results['omega'][0]],
                  mode='markers',
                  marker=dict(size=10, color='red', symbol='star'),
                  name='Current State',
                  showlegend=False),
        row=1, col=2
    )
    
    # Add angular velocity plot
    fig.add_trace(
        go.Scatter(x=t, y=results['omega'],
                  name='Angular velocity', line=dict(color='red', dash='solid'),
                  showlegend=False),
        row=2, col=1
    )
    
    # Add energy plots
    fig.add_trace(
        go.Scatter(x=t, y=results['kinetic_energy'],
                  name='Kinetic', line=dict(color='green')),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=t, y=results['potential_energy'],
                  name='Potential', line=dict(color='orange')),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=t, y=results['total_energy'],
                  name='Total', line=dict(color='black')),
        row=2, col=2
    )
    
    # Add vertical line shapes for time indicators
    shapes = []
    yranges = [
        [min(results['theta']), max(results['theta'])],  # Angle plot
        None,  # No time indicator for phase plot
        [min(results['omega']), max(results['omega'])],  # Angular velocity plot
        [0, max(results['total_energy'])]  # Energy plot
    ]
    
    # Add time indicators for plots vs time
    for i, yrange in enumerate(yranges):
        if yrange is not None:  # Skip phase plot
            shapes.append(dict(
                type='line',
                x0=0, x1=0,
                y0=yrange[0], y1=yrange[1],
                xref=f'x{i+1}', yref=f'y{i+1}',
                line=dict(color='red', width=2, dash='dot')
            ))
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        margin=dict(l=20, r=20, t=40, b=20),
        shapes=shapes
    )
    
    # Add subplot labels
    fig.update_xaxes(title_text='Time (s)', row=1, col=1)
    fig.update_xaxes(title_text='Angle (rad)', row=1, col=2)
    fig.update_xaxes(title_text='Time (s)', row=2, col=1)
    fig.update_xaxes(title_text='Time (s)', row=2, col=2)
    
    fig.update_yaxes(title_text='Angle (rad)', row=1, col=1)
    fig.update_yaxes(title_text='Angular Velocity (rad/s)', row=1, col=2)
    fig.update_yaxes(title_text='Angular Velocity (rad/s)', row=2, col=1)
    fig.update_yaxes(title_text='Energy (J)', row=2, col=2)
    
    # Update phase plot appearance
    fig.update_xaxes(row=1, col=2, zeroline=True, zerolinewidth=1, zerolinecolor='gray')
    fig.update_yaxes(row=1, col=2, zeroline=True, zerolinewidth=1, zerolinecolor='gray')
    
    return fig

def update_animation_frame(fig_anim, fig_plots, results, frame):
    """Update animation and plot figures to current frame."""
    with fig_anim.batch_update():
        # Update rod
        fig_anim.data[0].x = [0, results['x'][frame]]
        fig_anim.data[0].y = [0, results['y'][frame]]
        # Update bob
        fig_anim.data[1].x = [results['x'][frame]]
        fig_anim.data[1].y = [results['y'][frame]]
        
    with fig_plots.batch_update():
        # Update time indicators
        current_t = results['t'][frame]
        for shape in fig_plots.layout.shapes:
            shape.x0 = current_t
            shape.x1 = current_t
            
        # Update current state marker in phase plot
        # Phase plot state marker is the 3rd trace (index 2)
        fig_plots.data[2].x = [results['theta'][frame]]
        fig_plots.data[2].y = [results['omega'][frame]]