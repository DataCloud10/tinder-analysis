import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_city_distribution_chart(df, top_n=15):
    """
    Create horizontal bar chart for city distribution
    """
    city_counts = df['city_clean'].value_counts().head(top_n)
    city_counts = city_counts.sort_values(ascending=True)  # Per visualizzare dall'alto verso il basso
    
    fig = px.bar(
        x=city_counts.values,
        y=city_counts.index,
        orientation='h',
        title=f'Top {top_n} Cities',
        labels={'x': 'Number of Users', 'y': 'City'},
        color=city_counts.values,
        color_continuous_scale='viridis'
    )
    
    # Aggiusta il layout
    fig.update_layout(
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'},
        height=600
    )
    
    return fig

def create_completeness_chart(df):
    """
    Create bar chart for profile completeness
    """
    completeness = {
        'Bio': df['bio'].notna().mean() * 100,
        'City': df['city'].notna().mean() * 100,
        'Job': df['jobs'].notna().mean() * 100,
        'School': df['schools'].notna().mean() * 100,
        'Instagram': df['instagram'].notna().mean() * 100,
        'Spotify': df['spotify'].notna().mean() * 100
    }
    
    # Sort by completeness percentage
    completeness = dict(sorted(completeness.items(), key=lambda x: x[1], reverse=True))
    
    fig = px.bar(
        x=list(completeness.keys()),
        y=list(completeness.values()),
        title='Profile Completeness (%)',
        labels={'x': 'Field', 'y': 'Completeness (%)'},
        color=list(completeness.values()),
        color_continuous_scale=['red', 'yellow', 'green']
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        height=500
    )
    
    return fig

def create_age_distribution_chart(df):
    """
    Create bar chart for age distribution
    """
    if 'birth_date' not in df.columns:
        return go.Figure()
    
    try:
        df['age'] = pd.to_datetime('now').year - pd.to_datetime(df['birth_date']).dt.year
        
        age_bins = [18, 23, 28, 33, 38, 43, 100]
        age_labels = ['18-23', '24-28', '29-33', '34-38', '39-43', '44+']
        
        df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)
        age_dist = df['age_group'].value_counts().sort_index()
        
        fig = px.bar(
            x=age_dist.index,
            y=age_dist.values,
            title='Age Distribution',
            labels={'x': 'Age Group', 'y': 'Number of Users'},
            color=age_dist.values,
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(height=500)
        return fig
    except:
        return go.Figure()

def create_time_distribution_chart(time_periods):
    """
    Create donut chart for time distribution
    """
    fig = go.Figure(data=[go.Pie(
        labels=list(time_periods.keys()),
        values=list(time_periods.values()),
        hole=.3,
        marker_colors=['#2c3e50', '#3498db', '#2ecc71', '#e74c3c']
    )])
    
    fig.update_layout(
        title='Activity by Time Period',
        annotations=[dict(text='Time', x=0.5, y=0.5, font_size=20, showarrow=False)],
        height=500
    )
    
    return fig