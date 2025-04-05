import dash
from dash import html, dcc, dash_table, Input, Output, callback
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime

from metrics import *

# Configuration file to store the monitored coin
CONFIG_FILE = 'config.json'

# Function to get the configured coin
def get_configured_coin():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('coin', 'bitcoin')
    except Exception as e:
        print(f"Error reading config file: {e}")
    return 'bitcoin'

# Function to create price chart
def create_price_chart(prices_df, coin):
    fig = px.line(prices_df, x='snapped_at', y='price', 
                 title=f'{coin.capitalize()} Price Evolution',
                 labels={'snapped_at': 'Date', 'price': 'Price'},
                 template='plotly_white')
    
    fig.update_layout(
        xaxis=dict(
            title='Date',
            tickfont=dict(size=14),
            showgrid=True,
            gridcolor='lightgray',
        ),
        yaxis=dict(
            title='Price (USD)',
            tickfont=dict(size=14),
            showgrid=True,
            gridcolor='lightgray',
        ),
        plot_bgcolor='white',
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig

# Function to create metrics display
def create_metrics_display(metrics, coin):
    colors = {
        'text_dark': '#1f2937',
        'text_light': '#6b7280',
        'primary': '#3b82f6'
    }
    
    metrics_layout = []
    for metric_name, metric_value in metrics.items():
        metrics_layout.append(
            html.Div([
                html.H4(
                    metric_name, 
                    style={
                        'color': colors['text_light'], 
                        'marginBottom': '5px', 
                        'fontSize': '0.9rem'
                    }
                ),
                html.P(
                    f'{metric_value:.2f}', 
                    style={
                        'color': colors['text_dark'], 
                        'fontWeight': '600', 
                        'fontSize': '1.2rem'
                    }
                )
            ], style={
                'textAlign': 'center', 
                'padding': '10px', 
                'width': '200px'
            })
        )
    
    return metrics_layout

# Load CSV data
def load_data():
    coin = get_configured_coin()
    try:
        stats_df = pd.read_csv("stats.csv")
        prices_df = pd.read_csv("prices.csv")
        prices_df['snapped_at'] = pd.to_datetime(prices_df['snapped_at'])
        
        # Get last modified time of csv files
        if os.path.exists("stats.csv") and os.path.exists("prices.csv"):
            stats_mod_time = os.path.getmtime("stats.csv")
            last_mod_time = stats_mod_time
            last_updated = datetime.fromtimestamp(last_mod_time).strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_updated = "Unknown"
            
        return stats_df, prices_df, coin, last_updated
    except Exception as e:
        print(f"Error loading CSV files: {e}")
        return pd.DataFrame(), pd.DataFrame(columns=['snapped_at', 'price']), coin, "Error loading data"

# Initial data load
stats_df, prices_df, configured_coin, last_updated = load_data()

# Initialize the Dash app with a custom stylesheet
app = dash.Dash(__name__, external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap'
])

# Set up app to be deployed as a WSGI application
server = app.server

# Color palette
colors = {
    'background': '#f4f6f9',
    'card_background': '#ffffff',
    'primary': '#3b82f6',
    'text_dark': '#1f2937',
    'text_light': '#6b7280',
    'border': '#e5e7eb'
}

# Custom styles and layout without the refresh button.
app.layout = html.Div([
    html.Div([
        html.H1(
            id='dashboard-title',
            children=f"{configured_coin.capitalize()} Dashboard", 
            style={
                'color': colors['text_dark'], 
                'fontWeight': '600', 
                'marginBottom': '20px',
                'fontSize': '2.5rem'
            }
        ),
        html.P(
            "Real-time cryptocurrency data and analytics",
            style={
                'color': colors['text_light'], 
                'marginBottom': '10px',
                'fontSize': '1rem'
            }
        ),
        html.P(
            f"Last updated: {last_updated}",
            id='last-updated',
            style={
                'color': colors['primary'], 
                'marginBottom': '30px',
                'fontSize': '0.9rem',
                'fontWeight': '600'
            }
        ),
        # Interval component to update the dashboard every 10 seconds
        dcc.Interval(
            id='interval-component',
            interval=10000,
            n_intervals=0
        )
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    # Price Evolution Chart
    html.Div([
        dcc.Graph(
            id='price-evolution-chart',
            figure=create_price_chart(prices_df, configured_coin)
        )
    ], style={'padding': '0 20px', 'marginBottom': '30px'}),
    
    # Financial Metrics Section
    html.Div([
        html.Div(
            create_metrics_display(calculate_financial_metrics(prices_df), configured_coin),
            id='financial-metrics',
            style={
                'display': 'flex',
                'justifyContent': 'space-around',
                'flexWrap': 'wrap',
                'backgroundColor': colors['card_background'],
                'borderRadius': '12px',
                'padding': '20px',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
            }
        )
    ], style={'padding': '0 20px', 'marginBottom': '30px'}),
    
    html.Div([
        dash_table.DataTable(
            id='stats-table',
            columns=[{"name": i, "id": i} for i in stats_df.columns],
            data=stats_df.to_dict('records'),
            style_cell={
                'textAlign': 'left', 
                'padding': '12px',
                'fontFamily': 'Inter, sans-serif',
                'color': colors['text_dark']
            },
            style_header={
                'backgroundColor': colors['border'], 
                'fontWeight': '600',
                'color': colors['text_dark'],
                'border': 'none',
                'textTransform': 'uppercase',
                'fontSize': '0.85rem'
            },
            style_table={
                'overflowX': 'auto',
                'borderRadius': '12px',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': colors['background']
                }
            ]
        )
    ], style={'padding': '0 20px'})
], style={
    'backgroundColor': colors['background'], 
    'minHeight': '100vh', 
    'fontFamily': 'Inter, sans-serif',
    'padding': '20px'
})

# Callback for auto-updating the dashboard using the Interval component.
@app.callback(
    [
        Output('last-updated', 'children'),
        Output('price-evolution-chart', 'figure'),
        Output('financial-metrics', 'children'),
        Output('stats-table', 'data'),
        Output('dashboard-title', 'children')
    ],
    Input('interval-component', 'n_intervals')
)
def refresh_data(n_intervals):
    # Reload all data from CSV files
    stats_df, prices_df, coin, last_updated = load_data()
    
    # Calculate financial metrics
    metrics = calculate_financial_metrics(prices_df)
    
    # Create updated chart
    fig = create_price_chart(prices_df, coin)
    
    # Create updated metrics display
    metrics_display = create_metrics_display(metrics, coin)
    
    # Return all updated components
    return (
        f"Last updated: {last_updated}",  # Update timestamp
        fig,                              # Update price chart
        metrics_display,                  # Update metrics
        stats_df.to_dict('records'),      # Update table data
        f"{coin.capitalize()} Dashboard"   # Update title with current coin
    )

# Run the app.
if __name__ == '__main__':
    import logging
    logging.getLogger('werkzeug').disabled = True
    app.run(host='0.0.0.0', port=8050, debug=False)
