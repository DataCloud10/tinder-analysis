from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os
from pathlib import Path

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.data_processing import preprocess_data

def calculate_completeness(df):
    """Calcola la percentuale di completezza per ogni campo"""
    # Lista di colonne da escludere
    exclude_columns = ['original_id', 'original_userId', 'createdAt', 'city_clean']
    
    # Calcola la completezza per tutte le colonne eccetto quelle da escludere
    completeness = []
    for column in df.columns:
        if column not in exclude_columns:
            percentage = round(df[column].notna().mean() * 100, 1)
            completeness.append({
                'Field': column,
                'Percentage': percentage
            })
    
    # Converti in DataFrame, ordina per percentuale decrescente e prendi i top 15
    completeness_df = pd.DataFrame(completeness)
    return completeness_df.sort_values('Percentage', ascending=False).head(15)

def create_app():
    # Initialize the Dash app
    app = Dash(__name__)
    
    # Load data
    print("Loading data...")
    data_path = os.path.join(project_root, 'data', 'filtered_dump.csv')
    df = preprocess_data(data_path)
    print(f"Data loaded successfully! Total records: {len(df)}")

    # Calculate completeness data
    completeness_data = calculate_completeness(df)

    app.layout = html.Div(children=[
        # Header with bigger title and subtitle
        html.Div([
            html.H1(
                children='Tinder Data Analysis',
                style={
                    'textAlign': 'center', 
                    'color': '#2c3e50',
                    'fontSize': '48px',
                    'fontWeight': 'bold',
                    'marginBottom': '10px'
                }
            ),
            html.P(
                "Interactive Analysis of User Demographics and Behavior",
                style={
                    'textAlign': 'center',
                    'color': '#7f8c8d',
                    'fontSize': '20px',
                    'marginBottom': '30px'
                }
            ),
        ]),

        # Metrics
        html.Div([
            html.Div([
                html.H2(f"{len(df):,}", style={'color': '#3498db'}),
                html.P("Total Users")
            ], className='metric-box'),
            html.Div([
                html.H2(f"{df['bio'].notna().sum():,}", style={'color': '#2ecc71'}),
                html.P("Users with Bio")
            ], className='metric-box'),
            html.Div([
                html.H2(f"{df['age_verification'].notna().sum():,}", style={'color': '#e74c3c'}),
                html.P("Verified Users")
            ], className='metric-box'),
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px'}),

        # First row of graphs
        html.Div([
            # City Distribution
            html.Div([
                dcc.Graph(
                    figure=px.bar(
                        df['city_clean'].value_counts().head(15).sort_values(ascending=True),
                        orientation='h',
                        title='Top 15 Cities',
                        color=df['city_clean'].value_counts().head(15).sort_values(ascending=True),
                        color_continuous_scale='Viridis',
                        labels={'value': 'Number of Users', 'city_clean': 'City', 'color': 'Users'}
                    ).update_layout(
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0),
                        title_x=0.5,
                        title_font_size=20,
                        coloraxis_showscale=False
                    )
                )
            ], style={'width': '50%', 'display': 'inline-block'}),

            # Profile Completeness
            html.Div([
                dcc.Graph(
                    figure=px.bar(
                        completeness_data,
                        x='Field',
                        y='Percentage',
                        title='Profile Completeness (%)',
                        color='Percentage',
                        color_continuous_scale=[
                            [0, '#ff4d4d'],
                            [0.5, '#ffdd99'],
                            [1, '#66cc66']
                        ],
                    ).update_layout(
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0),
                        title_x=0.5,
                        title_font_size=20,
                        coloraxis_showscale=False,
                        xaxis_tickangle=-45,
                        yaxis_range=[0, 100],
                        bargap=0.3,  # Aumentato spazio tra le barre
                        uniformtext=dict(minsize=14, mode='show')  # Testo uniforme e più grande
                    ).update_traces(
                        text=completeness_data['Percentage'].astype(str) + '%',
                        textposition='inside',
                        textfont=dict(size=14, color='black'),  # Font size aumentato
                        marker=dict(
                            line=dict(color='white', width=1)
                        ),
                        width=0.7  # Larghezza delle barre ridotta per più spazio
                    )
                )
            ], style={'width': '50%', 'display': 'inline-block'})
        ]),

        # Second row of graphs
        html.Div([
            # Age Distribution
            html.Div([
                dcc.Graph(
                    figure=px.histogram(
                        df,
                        x=pd.to_datetime('now').year - pd.to_datetime(df['birth_date']).dt.year,
                        title='Age Distribution',
                        nbins=20,
                        color_discrete_sequence=['#FF69B4'],
                        labels={'x': 'Age', 'y': 'Count'}
                    ).update_layout(
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0),
                        title_x=0.5,
                        title_font_size=20,
                        showlegend=False,
                        bargap=0.1
                    ).update_traces(
                        marker=dict(
                            line=dict(color='rgba(255, 255, 255, 0.5)', width=1)
                        ),
                        opacity=0.7
                    )
                )
            ], style={'width': '50%', 'display': 'inline-block'}),

            # Gender Distribution
            html.Div([
                dcc.Graph(
                    figure=go.Figure(data=[go.Pie(
                        labels=['Male', 'Female'],
                        values=df['gender'].value_counts().values,
                        hole=0.4,
                        marker_colors=['#4a90e2', '#e8666f'],
                        textinfo='percent',
                        textfont_size=20,
                        textposition='outside',
                        pull=[0.05, 0.05],
                        hoverinfo='label+percent+value',
                        texttemplate='%{percent:.1f}%'
                    )]).update_layout(
                        title='Gender Distribution',
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0),
                        title_x=0.5,
                        title_font_size=20,
                        showlegend=True,
                        legend=dict(
                            font=dict(size=14),
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        annotations=[dict(
                            text='Gender<br>Split',
                            x=0.5,
                            y=0.5,
                            font_size=16,
                            showarrow=False
                        )]
                    )
                )
            ], style={'width': '50%', 'display': 'inline-block'})
        ])
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa'})

    return app

if __name__ == '__main__':
    print("Creating Dash app...")
    app = create_app()
    print("Starting server...")
    app.run_server(debug=False, port=8050)
    print("Server is running on http://localhost:8050")