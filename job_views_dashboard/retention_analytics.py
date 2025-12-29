import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import calendar
import numpy as np

# --- 1. COLOR THEMES ---
CARD_THEMES = {
    'black': {'bg': 'linear-gradient(135deg, #212529 0%, #343a40 100%)', 'text': '#ffffff'},
    'blue': {'bg': 'linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%)', 'text': '#ffffff'},
    'purple': {'bg': 'linear-gradient(135deg, #6f42c1 0%, #59359a 100%)', 'text': '#ffffff'},
    'red': {'bg': 'linear-gradient(135deg, #dc3545 0%, #b02a37 100%)', 'text': '#ffffff'},
    'green': {'bg': 'linear-gradient(135deg, #198754 0%, #146c43 100%)', 'text': '#ffffff'},
    'orange': {'bg': 'linear-gradient(135deg, #fd7e14 0%, #e35d0b 100%)', 'text': '#ffffff'},
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
        dbc.Col(html.H3("Retention & Repeat Posting Analysis", className="my-4",
                        style={'fontWeight': '800', 'color': '#2c3e50'}), width=12)
    ]),

    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Date Range", className="fw-bold small text-muted"),
            dcc.DatePickerRange(id='ret-date-picker', display_format='YYYY-MM-DD', clearable=True,
                                style={'width': '100%', 'borderRadius': '8px'})
        ], width=12, md=3),
        dbc.Col([
            html.Label("Country", className="fw-bold small text-muted"),
            dcc.Dropdown(id='ret-country-dropdown', multi=True, placeholder="All Countries")
        ], width=12, md=3),
        dbc.Col([
            html.Label("Job Category", className="fw-bold small text-muted"),
            dcc.Dropdown(id='ret-category-dropdown', multi=True, placeholder="All Categories")
        ], width=12, md=3),
        dbc.Col([
            html.Label("Company", className="fw-bold small text-muted"),
            dcc.Dropdown(id='ret-company-dropdown', multi=True, placeholder="All Companies")
        ], width=12, md=3),
    ], className="p-4 mb-4 bg-white shadow-sm", style={'borderRadius': '15px', 'borderLeft': '5px solid #6f42c1'}),

    # --- KPI CARDS ---
    dbc.Row([
        dbc.Col(create_solid_card("ret-rate", "Retention Rate", "0%", "% Companies Active > 30 Days", "purple"),
                width=12, sm=6, lg=3, className="mb-4"),
        dbc.Col(create_solid_card("ret-count", "Retained Companies", "0", "Posted across >1 Month", "blue"), width=12,
                sm=6, lg=3, className="mb-4"),
        dbc.Col(create_solid_card("ret-churn", "Single-Month Users", "0", "Active < 30 Days", "red"), width=12, sm=6,
                lg=3, className="mb-4"),
        dbc.Col(create_solid_card("ret-impact", "Retention Driver", "-", "Performance Impact", "green"), width=12, sm=6,
                lg=3, className="mb-4"),
    ]),

    # --- GRAPHS ---
    dbc.Row([
        # Graph 1: The "Why" - Performance Comparison
        dbc.Col(dbc.Card([
            dbc.CardHeader("1. Why do they return? (Avg Performance: Retained vs Single-Month)",
                           className="bg-transparent fw-bold border-0"),
            dbc.CardBody([
                html.Small("Comparing average Applications and Views per job for Retained vs Single-Month companies.",
                           className="text-muted"),
                dcc.Graph(id='ret-performance-graph', style={'height': '350px'}, config={'displayModeBar': False})
            ])
        ], style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': 'none'},
            className="mb-4"), width=12, lg=6),

        # Graph 2: Posting Frequency Distribution
        dbc.Col(dbc.Card([
            dbc.CardHeader("2. Posting Frequency (Loyalty Distribution)", className="bg-transparent fw-bold border-0"),
            dbc.CardBody([
                html.Small("How many jobs do companies typically post?", className="text-muted"),
                dcc.Graph(id='ret-freq-graph', style={'height': '350px'}, config={'displayModeBar': False})
            ])
        ], style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': 'none'},
            className="mb-4"), width=12, lg=6),
    ]),

    # --- TABLE ---
    dbc.Row([
        dbc.Col([
            html.H5("Top Retained Companies (Active > 1 Month)", className="mb-3 text-muted fw-bold"),
            html.Div(id='ret-table-container', style={'background': 'white', 'padding': '20px', 'borderRadius': '12px',
                                                      'boxShadow': '0 4px 12px rgba(0,0,0,0.05)'})
        ], width=12)
    ], className="mb-5")

], fluid=True)


# --- 4. CALLBACKS ---
def register_callbacks(app):
    # --- 1. Populate Dropdowns ---
    @app.callback(
        [Output('ret-country-dropdown', 'options'),
         Output('ret-category-dropdown', 'options'),
         Output('ret-company-dropdown', 'options')],
        Input('global-data-store', 'data')
    )
    def update_filters(data):
        if not data: return [], [], []
        df = pd.DataFrame(data)

        countries = [{'label': c, 'value': c} for c in
                     sorted(df['Country'].dropna().unique().astype(str))] if 'Country' in df.columns else []
        cats = [{'label': c, 'value': c} for c in
                sorted(df['Job_Category'].dropna().unique().astype(str))] if 'Job_Category' in df.columns else []
        comps = [{'label': c, 'value': c} for c in
                 sorted(df['Company'].dropna().unique().astype(str))] if 'Company' in df.columns else []

        return countries, cats, comps

    # --- 2. Update Analytics ---
    @app.callback(
        [
            Output('ret-rate', 'children'),
            Output('ret-count', 'children'),
            Output('ret-churn', 'children'),
            Output('ret-impact', 'children'),
            Output('ret-performance-graph', 'figure'),
            Output('ret-freq-graph', 'figure'),
            Output('ret-table-container', 'children')
        ],
        [
            Input('global-data-store', 'data'),
            Input('ret-date-picker', 'start_date'),
            Input('ret-date-picker', 'end_date'),
            Input('ret-country-dropdown', 'value'),
            Input('ret-category-dropdown', 'value'),
            Input('ret-company-dropdown', 'value')
        ]
    )
    def update_analytics(data, start_date, end_date, selected_countries, selected_cats, selected_comps):
        empty_fig = px.bar(title="No Data")

        # Helper for Card Content
        def make_content(title, val, sub):
            return [
                html.H6(title, className="text-uppercase fw-bold",
                        style={'fontSize': '0.75rem', 'opacity': '0.9', 'marginBottom': '5px'}),
                html.H2(val, className="fw-bold", style={'margin': '5px 0', 'fontSize': '2rem'}),
                html.Small(sub, style={'fontSize': '0.8rem', 'opacity': '0.8'})
            ]

        if not data:
            return [make_content(*x) for x in [
                ("Retention Rate", "0%", "N/A"), ("Retained Companies", "0", "N/A"),
                ("Single-Month Users", "0", "N/A"), ("Retention Driver", "-", "N/A")
            ]] + [empty_fig, empty_fig, None]

        df = pd.DataFrame(data)

        # --- PREPROCESSING ---
        if 'Created_At' in df.columns:
            df['Created_At'] = pd.to_datetime(df['Created_At'], errors='coerce')

        for col in ['Total_Applications', 'Total_Views']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # --- FILTERING ---
        if start_date and 'Created_At' in df.columns:
            df = df[df['Created_At'].dt.date >= pd.to_datetime(start_date).date()]
        if end_date and 'Created_At' in df.columns:
            df = df[df['Created_At'].dt.date <= pd.to_datetime(end_date).date()]
        if selected_countries and 'Country' in df.columns:
            df = df[df['Country'].isin(selected_countries)]
        if selected_cats and 'Job_Category' in df.columns:
            df = df[df['Job_Category'].isin(selected_cats)]
        if selected_comps and 'Company' in df.columns:
            df = df[df['Company'].isin(selected_comps)]

        if df.empty or 'Company' not in df.columns:
            return [make_content(*x) for x in [
                ("Retention Rate", "0%", "N/A"), ("Retained Companies", "0", "N/A"),
                ("Single-Month Users", "0", "N/A"), ("Retention Driver", "-", "N/A")
            ]] + [empty_fig, empty_fig, None]

        # --- RETENTION LOGIC (UPDATED) ---

        # 1. Group by Company to get First and Last Post Date
        company_stats = df.groupby('Company').agg({
            'Job_Title': 'count',  # Total Jobs
            'Total_Applications': 'sum',  # Total Apps
            'Total_Views': 'sum',  # Total Views
            'Created_At': ['min', 'max']  # First and Last Post Date
        }).reset_index()

        # Flatten MultiIndex columns
        company_stats.columns = ['Company', 'Job_Count', 'Total_Apps', 'Total_Views', 'First_Post', 'Last_Post']

        # Calculate Active Duration in Days
        company_stats['Active_Days'] = (company_stats['Last_Post'] - company_stats['First_Post']).dt.days

        # Calculate Averages per Company
        company_stats['Avg_Apps_Per_Job'] = company_stats['Total_Apps'] / company_stats['Job_Count']
        company_stats['Avg_Views_Per_Job'] = company_stats['Total_Views'] / company_stats['Job_Count']

        # 2. Segment Companies based on > 30 Days Activity
        # Retained = Active for more than 30 days (posted across > 1 month)
        retained_companies = company_stats[company_stats['Active_Days'] > 30]
        onetime_companies = company_stats[company_stats['Active_Days'] <= 30]

        # 3. KPI Calculations
        total_companies = len(company_stats)
        retained_count = len(retained_companies)
        onetime_count = len(onetime_companies)

        retention_rate = (retained_count / total_companies * 100) if total_companies > 0 else 0

        # 4. Driver Analysis (Why do they retain?)
        # Compare Avg Apps of Retained vs One-Time
        avg_apps_retained = retained_companies['Avg_Apps_Per_Job'].mean() if not retained_companies.empty else 0
        avg_apps_onetime = onetime_companies['Avg_Apps_Per_Job'].mean() if not onetime_companies.empty else 0

        avg_views_retained = retained_companies['Avg_Views_Per_Job'].mean() if not retained_companies.empty else 0
        avg_views_onetime = onetime_companies['Avg_Views_Per_Job'].mean() if not onetime_companies.empty else 0

        # Determine the driver text
        if avg_apps_retained > avg_apps_onetime:
            diff = ((avg_apps_retained - avg_apps_onetime) / avg_apps_onetime * 100) if avg_apps_onetime > 0 else 100
            driver_text = f"+{diff:.0f}% More Apps"
            driver_sub = "Retained get more Apps"
        elif avg_views_retained > avg_views_onetime:
            diff = ((
                                avg_views_retained - avg_views_onetime) / avg_views_onetime * 100) if avg_views_onetime > 0 else 100
            driver_text = f"+{diff:.0f}% More Views"
            driver_sub = "Retained get more Views"
        else:
            driver_text = "No Advantage"
            driver_sub = "Performance similar"

        # --- GRAPHS ---

        # Graph 1: Performance Comparison (Grouped Bar)
        perf_data = [
            {'Type': 'Retained (>30 Days)', 'Metric': 'Avg Applications', 'Value': avg_apps_retained},
            {'Type': 'Single-Month (<=30 Days)', 'Metric': 'Avg Applications', 'Value': avg_apps_onetime},
            {'Type': 'Retained (>30 Days)', 'Metric': 'Avg Views', 'Value': avg_views_retained},
            {'Type': 'Single-Month (<=30 Days)', 'Metric': 'Avg Views', 'Value': avg_views_onetime},
        ]
        perf_df = pd.DataFrame(perf_data)

        fig_perf = px.bar(perf_df, x='Metric', y='Value', color='Type', barmode='group',
                          color_discrete_map={'Retained (>30 Days)': '#6f42c1', 'Single-Month (<=30 Days)': '#dc3545'},
                          template="plotly_white", text_auto='.1f')
        fig_perf.update_layout(margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)', legend_title=None)

        # Graph 2: Frequency Distribution (Histogram)
        conditions = [
            (company_stats['Job_Count'] == 1),
            (company_stats['Job_Count'].between(2, 5)),
            (company_stats['Job_Count'].between(6, 10)),
            (company_stats['Job_Count'] > 10)
        ]
        choices = ['1 Job', '2-5 Jobs', '6-10 Jobs', '10+ Jobs']
        company_stats['Freq_Label'] = np.select(conditions, choices, default='1 Job')

        freq_counts = company_stats['Freq_Label'].value_counts().reindex(choices).reset_index()
        freq_counts.columns = ['Posting Frequency', 'Company Count']

        fig_freq = px.bar(freq_counts, x='Posting Frequency', y='Company Count', text='Company Count',
                          template="plotly_white")
        fig_freq.update_traces(marker_color='#fd7e14', textposition='outside')
        fig_freq.update_layout(plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20))

        # --- TABLE ---
        # Show Retained Companies sorted by Job Count
        # Filter for Retained (>30 days active)
        table_df = retained_companies.sort_values('Job_Count', ascending=False)

        # Round columns for display
        table_df['Avg_Apps_Per_Job'] = table_df['Avg_Apps_Per_Job'].round(1)

        # Select columns to display (Added Total_Views)
        display_cols = ['Company', 'Job_Count', 'Total_Apps', 'Total_Views', 'Avg_Apps_Per_Job']

        table = dash_table.DataTable(
            data=table_df.head(50).to_dict('records'),
            columns=[{'name': i.replace('_', ' '), 'id': i} for i in display_cols],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'Segoe UI'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ]
        )

        return (
            make_content("Retention Rate", f"{retention_rate:.1f}%",
                         f"{retained_count} of {total_companies} Companies"),
            make_content("Retained Companies", f"{retained_count}", "Active > 30 Days"),
            make_content("Single-Month Users", f"{onetime_count}", "Active <= 30 Days"),
            make_content("Retention Driver", driver_text, driver_sub),
            fig_perf,
            fig_freq,
            table
        )