import dash
from dash import html, dcc, dash_table, Input, Output, State
import pandas as pd
import plotly.express as px
import subprocess
import json
import os

from metrics import *

# Configuration file to store last searched coin
CONFIG_FILE = 'config.json'

# Function to get the last searched coin
def get_last_coin():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('coin', 'bitcoin')
    except Exception as e:
        print(f"Error reading config file: {e}")
    return 'bitcoin'

# Function to save the last searched coin
def save_last_coin(coin):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'coin': coin}, f)
    except Exception as e:
        print(f"Error saving config file: {e}")

# Initial load of CSV data
stats_df = pd.read_csv("stats.csv")
prices_df = pd.read_csv("prices.csv")

# Convert dates to datetime
prices_df['snapped_at'] = pd.to_datetime(prices_df['snapped_at'])

# Get the last searched coin
last_coin = get_last_coin()

# Initialize the Dash app with a custom stylesheet
app = dash.Dash(__name__, external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap'
])

# Color palette
colors = {
    'background': '#f4f6f9',
    'card_background': '#ffffff',
    'primary': '#3b82f6',
    'text_dark': '#1f2937',
    'text_light': '#6b7280',
    'border': '#e5e7eb'
}

# Custom styles
app.layout = html.Div([
    html.Div([
        html.H1(
            "Cryptocurrency Dashboard", 
            style={
                'color': colors['text_dark'], 
                'fontWeight': '600', 
                'marginBottom': '20px',
                'fontSize': '2.5rem'
            }
        ),
        html.P(
            "Real-time cryptocurrency data from CoinGecko",
            style={
                'color': colors['text_light'], 
                'marginBottom': '30px',
                'fontSize': '1rem'
            }
        )
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    html.Div([
        html.Div([
            dcc.Input(
                id='coin-input',
                type='text',
                placeholder='Enter coin slug (e.g., bitcoin)',
                value=last_coin,  # Use last searched coin as default
                style={
                    'width': '300px', 
                    'padding': '10px',
                    'borderRadius': '8px',
                    'border': f'1px solid {colors["border"]}',
                    'marginRight': '15px'
                }
            ),
            html.Button(
                "Fetch Data", 
                id='scrape-button', 
                n_clicks=0,
                style={
                    'backgroundColor': colors['primary'], 
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'borderRadius': '8px',
                    'cursor': 'pointer',
                    'fontWeight': '600',
                    'transition': 'background-color 0.3s'
                }
            )
        ], style={
            'display': 'flex', 
            'justifyContent': 'center', 
            'alignItems': 'center',
            'marginBottom': '30px'
        })
    ]),
    
    # Price Evolution Chart
    html.Div([
        dcc.Graph(id='price-evolution-chart')
    ], style={'padding': '0 20px', 'marginBottom': '30px'}),
    
    # Financial Metrics Section
    html.Div([
        html.Div(id='financial-metrics', style={
            'display': 'flex',
            'justifyContent': 'space-around',
            'flexWrap': 'wrap',
            'backgroundColor': colors['card_background'],
            'borderRadius': '12px',
            'padding': '20px',
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
        })
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

# Define callback to update the table, chart, and financial metrics when button is clicked.
@app.callback(
    [Output('stats-table', 'data'),
     Output('price-evolution-chart', 'figure'),
     Output('financial-metrics', 'children')],
    Input('scrape-button', 'n_clicks'),
    State('coin-input', 'value')
)
def update_data(n_clicks, coin):
    # Save the last searched coin
    save_last_coin(coin)
    
    if n_clicks is None or n_clicks == 0:
        # Return the initial data if button hasn't been clicked.
        stats_df = pd.read_csv("stats.csv")
        prices_df = pd.read_csv("prices.csv")
        prices_df['snapped_at'] = pd.to_datetime(prices_df['snapped_at'])
        
        # Create price evolution chart
        fig = px.line(prices_df, x='snapped_at', y='price', 
                      title=f'{coin.capitalize()} Price Evolution',
                      labels={'snapped_at': 'Date', 'price': 'Price'},
                      template='plotly_white')
        
        # Calculate financial metrics
        metrics = calculate_financial_metrics(prices_df)
        metrics_divs = create_metrics_display(metrics, coin)
        
        return stats_df.to_dict('records'), fig, metrics_divs
    
    # Run the bash script with the provided coin slug.
    try:
        subprocess.run(["C:/Program Files/Git/git-bash.exe", "./script.sh", coin], check=True)
    except subprocess.CalledProcessError as e:
        print("Error running the script:", e)
        # Return the current CSV data in case of error.
        stats_df = pd.read_csv("stats.csv")
        prices_df = pd.read_csv("prices.csv")
        prices_df['snapped_at'] = pd.to_datetime(prices_df['snapped_at'])
        
        # Create price evolution chart
        fig = px.line(prices_df, x='snapped_at', y='price', 
                      title=f'{coin.capitalize()} Price Evolution',
                      labels={'snapped_at': 'Date', 'price': 'Price'},
                      template='plotly_white')
        
        # Calculate financial metrics
        metrics = calculate_financial_metrics(prices_df)
        metrics_divs = create_metrics_display(metrics, coin)
        
        return stats_df.to_dict('records'), fig, metrics_divs
    
    # After scraping, reload the CSV data.
    updated_stats_df = pd.read_csv("stats.csv")
    updated_prices_df = pd.read_csv("prices.csv")
    updated_prices_df['snapped_at'] = pd.to_datetime(updated_prices_df['snapped_at'])
    
    # Create price evolution chart
    fig = px.line(updated_prices_df, x='snapped_at', y='price', 
                  title=f'{coin.capitalize()} Price Evolution',
                  labels={'snapped_at': 'Date', 'price': 'Price'},
                  template='plotly_white')
    
    # Calculate financial metrics
    metrics = calculate_financial_metrics(updated_prices_df)
    metrics_divs = create_metrics_display(metrics, coin)
    
    return updated_stats_df.to_dict('records'), fig, metrics_divs

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

# Run the app.
if __name__ == '__main__':
    app.run(debug=True)