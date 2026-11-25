import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from prophet import Prophet
import numpy as np
from datetime import timedelta

# --- 1. COLOR THEMES ---
CARD_THEMES = {
    'black': {'bg': 'linear-gradient(135deg, #212529 0%, #343a40 100%)', 'text': '#ffffff'},
    'green': {'bg': 'linear-gradient(135deg, #198754 0%, #146c43 100%)', 'text': '#ffffff'},
    'purple': {'bg': 'linear-gradient(135deg, #6f42c1 0%, #59359a 100%)', 'text': '#ffffff'},
    'blue': {'bg': 'linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%)', 'text': '#ffffff'},
}


# --- 2. HELPER FUNCTION ---
def create_solid_card(card_id, title, value, subtext, theme_key):
    theme = CARD_THEMES.get(theme_key, CARD_THEMES['black'])
    return html.Div([
        html.H6(title, className="text-uppercase fw-bold",
                style={'fontSize': '0.75rem', 'opacity': '0.9', 'marginBottom': '5px'}),
        html.H2(value, className="fw-bold", style={'margin': '5px 0', 'fontSize': '2rem'}),
        html.Small(subtext, style={'fontSize': '0.8rem', 'opacity': '0.8'})
    ],
        id=card_id,
        style={
            'background': theme['bg'],
            'color': theme['text'],
            'borderRadius': '12px',
            'padding': '20px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
            'height': '100%',
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'center',
            'border': 'none'
        },
        className="kpi-card-hover"
    )


# --- 3. LAYOUT ---
layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col([
            html.H3("AI Forecast: Candidate Demand Prediction", className="my-4",
                    style={'fontWeight': '800', 'color': '#2c3e50'}),
            html.P("Predicting the volume of Job Applications for the next 30 days (Including Viral Spikes).",
                   className="text-muted")
        ], width=12)
    ]),

    # --- KPI CARDS ---
    dbc.Row([
        dbc.Col(create_solid_card("ai-app-last-30", "Actual Apps (Last 30 Days)", "0", "Historical Baseline", "black"),
                width=12, sm=6, lg=4, className="mb-4"),
        dbc.Col(create_solid_card("ai-app-next-30", "Projected Apps (Next 30 Days)", "0", "AI Prediction", "green"),
                width=12, sm=6, lg=4, className="mb-4"),
        dbc.Col(create_solid_card("ai-app-growth", "Predicted Demand Growth", "0%", "Trend Direction", "purple"),
                width=12, sm=6, lg=4, className="mb-4"),
    ]),

    # --- MAIN GRAPH ---
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("30-Day Application Volume Forecast", className="bg-transparent fw-bold border-0"),
            dbc.CardBody([
                dcc.Loading(
                    id="loading-app-forecast",
                    type="circle",
                    children=dcc.Graph(id='ai-app-forecast-graph', style={'height': '500px'},
                                       config={'displayModeBar': False})
                )
            ])
        ], style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': 'none'},
            className="mb-4"), width=12),
    ]),

], fluid=True)


# --- 4. CALLBACKS ---
def register_callbacks(app):
    @app.callback(
        [
            Output('ai-app-last-30', 'children'),
            Output('ai-app-next-30', 'children'),
            Output('ai-app-growth', 'children'),
            Output('ai-app-forecast-graph', 'figure')
        ],
        [Input('global-data-store', 'data')]
    )
    def update_app_forecast(data):
        # Default Empty State
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Not enough data to forecast")

        # Helper for Card Content
        def make_content(title, val, sub):
            return [
                html.H6(title, className="text-uppercase fw-bold",
                        style={'fontSize': '0.75rem', 'opacity': '0.9', 'marginBottom': '5px'}),
                html.H2(val, className="fw-bold", style={'margin': '5px 0', 'fontSize': '2rem'}),
                html.Small(sub, style={'fontSize': '0.8rem', 'opacity': '0.8'})
            ]

        if not data:
            return [make_content("Metric", "0", "-")] * 3 + [empty_fig]

        df = pd.DataFrame(data)

        # 1. Data Prep for Prophet
        if 'Created_At' not in df.columns or 'Total_Applications' not in df.columns:
            return [make_content("Metric", "0", "-")] * 3 + [empty_fig]

        df['Created_At'] = pd.to_datetime(df['Created_At'], errors='coerce')
        df['Total_Applications'] = pd.to_numeric(df['Total_Applications'], errors='coerce').fillna(0)

        # Group by Day to get Daily Application Sum
        daily_apps = df.groupby(df['Created_At'].dt.date)['Total_Applications'].sum().reset_index(name='y')
        daily_apps.columns = ['ds', 'y']
        daily_apps['ds'] = pd.to_datetime(daily_apps['ds'])

        if len(daily_apps) < 10:
            return [make_content("Error", "N/A", "Need more data")] * 3 + [empty_fig]

        # --- OUTLIER REMOVAL REMOVED ---
        # The code block to remove outliers has been deleted.
        # The model will now train on the full, raw dataset including spikes.
        # -------------------------------

        # 2. Train Prophet Model
        m = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
        m.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        m.fit(daily_apps)

        # 3. Make Future Dataframe (30 Days)
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)

        # 4. Calculate KPIs
        # Last 30 Days Actuals
        last_30_date = daily_apps['ds'].max() - timedelta(days=30)
        actual_last_30 = daily_apps[daily_apps['ds'] > last_30_date]['y'].sum()

        # Next 30 Days Prediction
        last_actual_date = daily_apps['ds'].max()
        predicted_next_30 = forecast[forecast['ds'] > last_actual_date]['yhat'].sum()

        # Growth Calculation
        if actual_last_30 > 0:
            growth = ((predicted_next_30 - actual_last_30) / actual_last_30) * 100
            growth_str = f"{growth:+.1f}%"
            growth_sub = "vs Previous 30 Days"
        else:
            growth_str = "N/A"
            growth_sub = "Insufficient History"

        # 5. Build Graph
        fig = go.Figure()

        # A. Historical Data (Green Line)
        fig.add_trace(go.Scatter(
            x=daily_apps['ds'],
            y=daily_apps['y'],
            mode='lines',
            name='Actual Applications',
            line=dict(color='#198754', width=2)
        ))

        # B. Forecast Data (Red Dashed Line)
        future_forecast = forecast[forecast['ds'] > last_actual_date]

        fig.add_trace(go.Scatter(
            x=future_forecast['ds'],
            y=future_forecast['yhat'],
            mode='lines',
            name='AI Forecast',
            line=dict(color='#dc3545', width=2, dash='dash')
        ))

        # C. Confidence Interval
        fig.add_trace(go.Scatter(
            x=future_forecast['ds'],
            y=future_forecast['yhat_upper'],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=future_forecast['ds'],
            y=future_forecast['yhat_lower'],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(220, 53, 69, 0.2)',
            name='Confidence Interval',
            hoverinfo='skip'
        ))

        fig.update_layout(
            template="plotly_white",
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified",
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False, title="Date"),
            yaxis=dict(showgrid=True, gridcolor='#eee', title="Application Volume")
        )

        return (
            make_content("Actual Apps (Last 30 Days)", f"{int(actual_last_30):,}", "Historical Baseline"),
            make_content("Projected Apps (Next 30 Days)", f"{int(predicted_next_30):,}", "AI Prediction"),
            make_content("Predicted Growth", growth_str, growth_sub),
            fig
        )