import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import calendar

# --- 1. COLOR THEMES (Defined in Python to ensure they load) ---
CARD_THEMES = {
    'black': {'bg': 'linear-gradient(135deg, #212529 0%, #343a40 100%)', 'text': '#ffffff'},
    'cyan': {'bg': 'linear-gradient(135deg, #0dcaf0 0%, #0aa2c0 100%)', 'text': '#ffffff'},
    'blue': {'bg': 'linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%)', 'text': '#ffffff'},
    'purple': {'bg': 'linear-gradient(135deg, #6f42c1 0%, #59359a 100%)', 'text': '#ffffff'},
    'red': {'bg': 'linear-gradient(135deg, #dc3545 0%, #b02a37 100%)', 'text': '#ffffff'},
    'green': {'bg': 'linear-gradient(135deg, #198754 0%, #146c43 100%)', 'text': '#ffffff'},
    'yellow': {'bg': 'linear-gradient(135deg, #ffc107 0%, #e0a800 100%)', 'text': '#212529'},  # Dark text
    'grey': {'bg': 'linear-gradient(135deg, #6c757d 0%, #495057 100%)', 'text': '#ffffff'},
}


# --- 2. HELPER FUNCTION ---
def create_solid_card(card_id, title, value, subtext, theme_key):
    """
    Creates a card with INLINE styles to guarantee colors appear.
    """
    theme = CARD_THEMES.get(theme_key, CARD_THEMES['black'])

    return html.Div([
        # Initial Content (Will be updated by Callback)
        html.H6(title, className="text-uppercase fw-bold",
                style={'fontSize': '0.8rem', 'opacity': '0.9', 'marginBottom': '5px'}),
        html.H2(value, className="fw-bold", style={'margin': '5px 0', 'fontSize': '2rem'}),
        html.Small(subtext, style={'fontSize': '0.8rem', 'opacity': '0.8'})
    ],
        id=card_id,
        # INLINE STYLES to bypass CSS caching issues
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
        className="kpi-card-hover"  # Only for hover effect (defined in CSS)
    )

# --- 3. LAYOUT ---
layout = dbc.Container([

    # Page Header
    dbc.Row([
        dbc.Col(html.H3("Country Jobs Posted", className="my-4", style={'fontWeight': '800', 'color': '#2c3e50'}),
                width=12)
    ]),

    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Date Range", className="fw-bold small text-muted"),
            dcc.DatePickerRange(id='cjp-date-picker', display_format='YYYY-MM-DD', clearable=True,
                                style={'width': '100%', 'borderRadius': '8px'})
        ], width=12, md=3),
        dbc.Col([
            html.Label("Month", className="fw-bold small text-muted"),
            dcc.Dropdown(id='cjp-month-dropdown',
                         options=[{'label': calendar.month_name[i], 'value': i} for i in range(1, 13)], multi=True,
                         placeholder="Select Months...")
        ], width=12, md=3),
        dbc.Col([
            html.Label("Country", className="fw-bold small text-muted"),
            dcc.Dropdown(id='cjp-country-dropdown', multi=True, placeholder="All Countries")
        ], width=12, md=3),
        dbc.Col([
            html.Label("Job Category", className="fw-bold small text-muted"),
            dcc.Dropdown(id='cjp-category-dropdown', multi=True, placeholder="All Categories")
        ], width=12, md=3),
    ], className="p-4 mb-4 bg-white shadow-sm", style={'borderRadius': '15px', 'borderLeft': '5px solid #0d6efd'}),

    # --- KPI CARDS (Using Inline Styles) ---
    dbc.Row([
        # Row 1
        dbc.Col(create_solid_card("cjp-total-jobs", "Total Jobs", "0", "Global Count", "black"), width=12, sm=6, lg=3,
                className="mb-4"),
        dbc.Col(create_solid_card("cjp-avg-country", "Avg per Country", "0", "Mean Value", "cyan"), width=12, sm=6,
                lg=3, className="mb-4"),
        dbc.Col(create_solid_card("cjp-active-countries", "Active Countries", "0", "Distinct Count", "blue"), width=12,
                sm=6, lg=3, className="mb-4"),
        dbc.Col(create_solid_card("cjp-market-share", "Top Market Share", "0%", "Dominance", "red"), width=12, sm=6,
                lg=3, className="mb-4"),
    ]),

    dbc.Row([
        # Row 2
        dbc.Col(create_solid_card("cjp-highest-country", "Highest Country", "-", "Max Posted", "green"), width=12, md=4,
                className="mb-4"),
        dbc.Col(create_solid_card("cjp-lowest-country", "Lowest Country", "-", "Min Posted", "yellow"), width=12, md=4,
                className="mb-4"),
        dbc.Col(create_solid_card("cjp-top3-markets", "Top 3 Markets", "-", "Country: Count", "grey"), width=12, md=4,
                className="mb-4"),
    ]),

    # Graphs
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Jobs Posted by Country (Top 20)", className="bg-transparent fw-bold border-0"),
            dbc.CardBody(dcc.Graph(id='cjp-bar-graph', style={'height': '350px'}, config={'displayModeBar': False}))
        ], style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': 'none'},
            className="mb-4"), width=12),
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Market Share Distribution", className="bg-transparent fw-bold border-0"),
            dbc.CardBody(dcc.Graph(id='cjp-pie-graph', style={'height': '400px'}, config={'displayModeBar': False}))
        ], style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': 'none'},
            className="mb-4"), width=12),
    ]),

    # Table
    dbc.Row([
        dbc.Col([
            html.H5("Top Countries Statistics", className="mb-3 text-muted fw-bold"),
            html.Div(id='cjp-table-container', style={'background': 'white', 'padding': '20px', 'borderRadius': '12px',
                                                      'boxShadow': '0 4px 12px rgba(0,0,0,0.05)'})
        ], width=12)
    ], className="mb-5")

], fluid=True)


# --- 4. CALLBACKS ---
def register_callbacks(app):
    # Filter Options
    @app.callback(
        [Output('cjp-country-dropdown', 'options'),
         Output('cjp-category-dropdown', 'options')],
        Input('global-data-store', 'data')
    )
    def update_filters(data):
        if not data: return [], []
        df = pd.DataFrame(data)
        countries = [{'label': c, 'value': c} for c in
                     sorted(df['Country'].dropna().unique().astype(str))] if 'Country' in df.columns else []
        cats = [{'label': c, 'value': c} for c in
                sorted(df['Job_Category'].dropna().unique().astype(str))] if 'Job_Category' in df.columns else []
        return countries, cats

    # Main Analytics
    @app.callback(
        [
            Output('cjp-total-jobs', 'children'),
            Output('cjp-avg-country', 'children'),
            Output('cjp-active-countries', 'children'),
            Output('cjp-market-share', 'children'),
            Output('cjp-highest-country', 'children'),
            Output('cjp-lowest-country', 'children'),
            Output('cjp-top3-markets', 'children'),
            Output('cjp-bar-graph', 'figure'),
            Output('cjp-pie-graph', 'figure'),
            Output('cjp-table-container', 'children')
        ],
        [
            Input('global-data-store', 'data'),
            Input('cjp-date-picker', 'start_date'),
            Input('cjp-date-picker', 'end_date'),
            Input('cjp-month-dropdown', 'value'),
            Input('cjp-country-dropdown', 'value'),
            Input('cjp-category-dropdown', 'value')
        ]
    )
    def update_analytics(data, start_date, end_date, selected_months, selected_countries, selected_cats):
        empty_fig = px.bar(title="No Data")

        # Helper: Returns simple HTML elements.
        # Colors are inherited from the parent container (set in Layout), so we don't set classes here.
        def make_content(title, val, sub):
            return [
                html.H6(title, className="text-uppercase fw-bold",
                        style={'fontSize': '0.75rem', 'opacity': '0.9', 'marginBottom': '5px'}),
                html.H2(val, className="fw-bold", style={'margin': '5px 0', 'fontSize': '2rem'}),
                html.Small(sub, style={'fontSize': '0.8rem', 'opacity': '0.8'})
            ]

        defaults = [
            ("Total Jobs", "0", "Global Count"),
            ("Avg per Country", "0", "Mean Value"),
            ("Active Countries", "0", "Distinct Count"),
            ("Top Market Share", "0%", "Dominance"),
            ("Highest Country", "-", "Max Posted"),
            ("Lowest Country", "-", "Min Posted"),
            ("Top 3 Markets", "-", "Country: Count")
        ]

        if not data:
            return [make_content(*x) for x in defaults] + [empty_fig, empty_fig, None]

        df = pd.DataFrame(data)

        # Preprocessing
        if 'Created_At' in df.columns:
            df['Created_At'] = pd.to_datetime(df['Created_At'], errors='coerce')
        for col in ['Total_Applications', 'Total_Views']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Filtering
        if start_date: df = df[df['Created_At'].dt.date >= pd.to_datetime(start_date).date()]
        if end_date: df = df[df['Created_At'].dt.date <= pd.to_datetime(end_date).date()]
        if selected_months: df = df[df['Created_At'].dt.month.isin(selected_months)]
        if selected_countries and 'Country' in df.columns: df = df[df['Country'].isin(selected_countries)]
        if selected_cats: df = df[df['Job_Category'].isin(selected_cats)]

        if df.empty or 'Country' not in df.columns:
            return [make_content(*x) for x in defaults] + [empty_fig, empty_fig, None]

        # Calculations
        total_jobs = len(df)
        country_counts = df['Country'].value_counts()

        if country_counts.empty:
            return [make_content(*x) for x in defaults] + [empty_fig, empty_fig, None]

        avg_per_country = round(country_counts.mean(), 1)
        active_countries = len(country_counts)

        max_val = country_counts.max()
        max_country = country_counts.idxmax()
        max_str = f"{max_val} ({max_country})"

        min_val = country_counts.min()
        min_country = country_counts.idxmin()
        min_str = f"{min_val} ({min_country})"

        share_pct = (max_val / total_jobs * 100)
        share_str = f"{share_pct:.1f}%"

        top3 = country_counts.head(3)
        top3_str = ", ".join([f"{idx}: {val}" for idx, val in top3.items()])

        # Graphs
        bar_df = country_counts.head(20).reset_index()
        bar_df.columns = ['Country', 'Jobs']
        fig_bar = px.bar(bar_df, x='Country', y='Jobs', text='Jobs', template="plotly_white")
        fig_bar.update_traces(marker_color='#0d6efd', textposition='outside')
        fig_bar.update_layout(margin=dict(l=20, r=20, t=20, b=50), plot_bgcolor='rgba(0,0,0,0)',
                              yaxis=dict(showgrid=True, gridcolor='#eee'))

        fig_pie = px.pie(bar_df.head(10), values='Jobs', names='Country', hole=0.4, template="plotly_white")
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), showlegend=True)

        # Table
        table_df = df.groupby('Country').agg({
            'Job_Title': 'count',
            'Total_Views': 'sum',
            'Total_Applications': 'sum'
        }).reset_index()
        table_df.columns = ['Country', 'Jobs Posted', 'Total Views', 'Total Applications']
        table_df = table_df.sort_values('Jobs Posted', ascending=False).head(50)

        table = dash_table.DataTable(
            data=table_df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in table_df.columns],
            page_size=10,
            style_table={'overflowX': 'auto', 'borderRadius': '8px', 'border': '1px solid #eee'},
            style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold', 'padding': '12px'},
            style_cell={'textAlign': 'left', 'padding': '12px', 'fontFamily': 'Segoe UI', 'fontSize': '14px'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 249, 250)'}]
        )

        return (
            make_content("Total Jobs", f"{total_jobs:,}", "Global Count"),
            make_content("Avg per Country", f"{avg_per_country}", "Mean Value"),
            make_content("Active Countries", f"{active_countries}", "Distinct Count"),
            make_content("Top Market Share", share_str, "Dominance"),
            make_content("Highest Country", max_str, "Max Posted"),
            make_content("Lowest Country", min_str, "Min Posted"),
            make_content("Top 3 Markets", top3_str, "Country: Count"),
            fig_bar,
            fig_pie,
            table
        )