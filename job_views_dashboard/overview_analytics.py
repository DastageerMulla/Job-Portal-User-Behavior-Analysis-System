import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

# --- 1. COLOR THEMES (Same as Country Page) ---
CARD_THEMES = {
    'black': {'bg': 'linear-gradient(135deg, #212529 0%, #343a40 100%)', 'text': '#ffffff'},
    'cyan': {'bg': 'linear-gradient(135deg, #0dcaf0 0%, #0aa2c0 100%)', 'text': '#ffffff'},
    'blue': {'bg': 'linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%)', 'text': '#ffffff'},
    'purple': {'bg': 'linear-gradient(135deg, #6f42c1 0%, #59359a 100%)', 'text': '#ffffff'},
    'red': {'bg': 'linear-gradient(135deg, #dc3545 0%, #b02a37 100%)', 'text': '#ffffff'},
    'green': {'bg': 'linear-gradient(135deg, #198754 0%, #146c43 100%)', 'text': '#ffffff'},
    'orange': {'bg': 'linear-gradient(135deg, #fd7e14 0%, #e35d0b 100%)', 'text': '#ffffff'},
    'yellow': {'bg': 'linear-gradient(135deg, #ffc107 0%, #e0a800 100%)', 'text': '#212529'},
    'grey': {'bg': 'linear-gradient(135deg, #6c757d 0%, #495057 100%)', 'text': '#ffffff'},
}


# --- 2. HELPER FUNCTIONS ---

def create_solid_card(card_id, title, value, subtext, theme_key):
    """
    Creates a card with INLINE styles to guarantee colors appear.
    """
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
        className="kpi-card-hover"  # Hover effect from CSS
    )


def create_graph_card(title, graph_id):
    """
    Creates a clean white card for graphs (Matches Country Page Style).
    """
    return dbc.Card([
        dbc.CardHeader(title, className="bg-transparent fw-bold border-0", style={'color': '#343a40'}),
        dbc.CardBody(dcc.Graph(id=graph_id, style={'height': '350px'}, config={'displayModeBar': False}))
    ], style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': 'none'}, className="mb-4")


# --- 3. LAYOUT DEFINITION ---

layout = dbc.Container([

    # 1. Page Header
    dbc.Row([
        dbc.Col(html.H3("Job Overview", className="my-4", style={'fontWeight': '800', 'color': '#2c3e50'}), width=12)
    ]),

    # 2. Filters (Styled like Country Page)
    dbc.Row([
        # Date Range
        dbc.Col([
            html.Label("Date Range", className="fw-bold small text-muted"),
            dcc.DatePickerRange(
                id='ov-date-picker',
                display_format='YYYY-MM-DD',
                clearable=True,
                style={'width': '100%', 'borderRadius': '8px'}
            )
        ], width=12, md=4),

        # Category
        dbc.Col([
            html.Label("Job Category", className="fw-bold small text-muted"),
            dcc.Dropdown(
                id='ov-category-dropdown',
                options=[],
                multi=True,
                placeholder="All Categories",
            )
        ], width=12, md=4),

        # Company
        dbc.Col([
            html.Label("Company", className="fw-bold small text-muted"),
            dcc.Dropdown(
                id='ov-company-dropdown',
                options=[],
                multi=True,
                placeholder="All Companies",
            )
        ], width=12, md=4),
    ], className="p-4 mb-4 bg-white shadow-sm", style={'borderRadius': '15px', 'borderLeft': '5px solid #0d6efd'}),

    # 3. KPI Cards (Solid Gradients)
    dbc.Row([
        dbc.Col(create_solid_card("ov-kpi-total-jobs", "Total Jobs", "0", "Posted Jobs", "blue"), width=12, sm=6, lg=2,
                className="mb-4"),
        dbc.Col(create_solid_card("ov-kpi-total-apps", "Total Apps", "0", "Applications", "green"), width=12, sm=6,
                lg=2, className="mb-4"),
        dbc.Col(create_solid_card("ov-kpi-total-views", "Total Views", "0", "Job Views", "cyan"), width=12, sm=6, lg=2,
                className="mb-4"),
        dbc.Col(create_solid_card("ov-kpi-avg-views", "Avg Views/Job", "0", "Per Posting", "purple"), width=12, sm=6,
                lg=2, className="mb-4"),
        dbc.Col(create_solid_card("ov-kpi-avg-apps", "Avg Apps/Job", "0", "Per Posting", "orange"), width=12, sm=6,
                lg=2, className="mb-4"),
        dbc.Col(create_solid_card("ov-kpi-conversion", "Conversion", "0%", "Apps / Views", "red"), width=12, sm=6, lg=2,
                className="mb-4"),
    ]),

    # 4. Graphs
    dbc.Row([
        dbc.Col(create_graph_card("Jobs Posted Trend", "ov-jobs-posted-graph"), width=12)
    ]),

    dbc.Row([
        dbc.Col(create_graph_card("Application Volume Trend", "ov-applications-time-graph"), width=12)
    ]),

    dbc.Row([
        dbc.Col(create_graph_card("View Traffic Trend", "ov-views-time-graph"), width=12)
    ]),

], fluid=True)


# --- 4. CALLBACKS ---

def register_callbacks(app):
    # --- Helper for Graph Styling ---
    def create_clean_line_chart(df, x_col, y_col, title, line_color, fill_color):
        fig = px.area(df, x=x_col, y=y_col, markers=True, template="plotly_white")
        fig.update_traces(
            line_color=line_color,
            line_shape='spline',
            line_width=3,
            fillcolor=fill_color,
            mode='lines+markers'
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            hovermode="x unified",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, title=None, showline=True, linecolor='#eee'),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', title=None),
        )
        return fig

    # --- Callback A: Populate Dropdowns ---
    @app.callback(
        [Output('ov-category-dropdown', 'options'),
         Output('ov-company-dropdown', 'options')],
        Input('global-data-store', 'data')
    )
    def update_dropdowns(data):
        if not data: return [], []
        df = pd.DataFrame(data)

        cat_opts = []
        if 'Job_Category' in df.columns:
            cats = sorted(df['Job_Category'].dropna().unique().astype(str))
            cat_opts = [{'label': c, 'value': c} for c in cats]

        comp_opts = []
        if 'Company' in df.columns:
            comps = sorted(df['Company'].dropna().unique().astype(str))
            comp_opts = [{'label': c, 'value': c} for c in comps]

        return cat_opts, comp_opts

    # --- Callback B: Update Metrics & Graphs ---
    @app.callback(
        [
            Output('ov-kpi-total-jobs', 'children'),
            Output('ov-kpi-total-apps', 'children'),
            Output('ov-kpi-total-views', 'children'),
            Output('ov-kpi-avg-views', 'children'),
            Output('ov-kpi-avg-apps', 'children'),
            Output('ov-kpi-conversion', 'children'),
            Output('ov-jobs-posted-graph', 'figure'),
            Output('ov-applications-time-graph', 'figure'),
            Output('ov-views-time-graph', 'figure')
        ],
        [
            Input('global-data-store', 'data'),
            Input('ov-date-picker', 'start_date'),
            Input('ov-date-picker', 'end_date'),
            Input('ov-category-dropdown', 'value'),
            Input('ov-company-dropdown', 'value')
        ]
    )
    def update_job_dashboard(data, start_date, end_date, selected_cats, selected_comps):
        empty_fig = px.line(title="No Data Available")
        empty_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')

        # Helper to reconstruct content (Same as Country Page logic)
        def make_content(title, val, sub):
            return [
                html.H6(title, className="text-uppercase fw-bold",
                        style={'fontSize': '0.75rem', 'opacity': '0.9', 'marginBottom': '5px'}),
                html.H2(val, className="fw-bold", style={'margin': '5px 0', 'fontSize': '2rem'}),
                html.Small(sub, style={'fontSize': '0.8rem', 'opacity': '0.8'})
            ]

        if not data:
            return [make_content(*x) for x in [
                ("Total Jobs", "0", "Posted Jobs"), ("Total Apps", "0", "Applications"),
                ("Total Views", "0", "Job Views"), ("Avg Views/Job", "0", "Per Posting"),
                ("Avg Apps/Job", "0", "Per Posting"), ("Conversion", "0%", "Apps / Views")
            ]] + [empty_fig, empty_fig, empty_fig]

        df = pd.DataFrame(data)

        # Data Processing
        cols_to_numeric = ['Total_Views', 'Total_Applications']
        for col in cols_to_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        if 'Created_At' in df.columns:
            df['Created_At'] = pd.to_datetime(df['Created_At'], errors='coerce')

        # Filters
        if start_date and 'Created_At' in df.columns:
            df = df[df['Created_At'].dt.date >= pd.to_datetime(start_date).date()]
        if end_date and 'Created_At' in df.columns:
            df = df[df['Created_At'].dt.date <= pd.to_datetime(end_date).date()]
        if selected_cats and 'Job_Category' in df.columns:
            df = df[df['Job_Category'].isin(selected_cats)]
        if selected_comps and 'Company' in df.columns:
            df = df[df['Company'].isin(selected_comps)]

        if df.empty:
            return [make_content(*x) for x in [
                ("Total Jobs", "0", "Posted Jobs"), ("Total Apps", "0", "Applications"),
                ("Total Views", "0", "Job Views"), ("Avg Views/Job", "0", "Per Posting"),
                ("Avg Apps/Job", "0", "Per Posting"), ("Conversion", "0%", "Apps / Views")
            ]] + [empty_fig, empty_fig, empty_fig]

        # KPI Calculations
        total_jobs = len(df)
        total_apps = int(df['Total_Applications'].sum())
        total_views = int(df['Total_Views'].sum())
        avg_views = round(total_views / total_jobs, 1) if total_jobs > 0 else 0
        avg_apps = round(total_apps / total_jobs, 1) if total_jobs > 0 else 0
        conversion_rate = (total_apps / total_views * 100) if total_views > 0 else 0
        conversion_str = f"{conversion_rate:.2f}%"

        # Graphs
        if 'Created_At' in df.columns:
            time_df = df.groupby(df['Created_At'].dt.date).agg({
                'Created_At': 'count',
                'Total_Applications': 'sum',
                'Total_Views': 'sum'
            }).rename(columns={'Created_At': 'Jobs_Count'}).reset_index()
            time_df.rename(columns={'Created_At': 'Date'}, inplace=True)

            # 1. Jobs (Blue)
            fig_jobs = create_clean_line_chart(
                time_df, 'Date', 'Jobs_Count', "Jobs",
                line_color="#0d6efd", fill_color="rgba(13, 110, 253, 0.1)"
            )

            # 2. Apps (Green)
            fig_apps = create_clean_line_chart(
                time_df, 'Date', 'Total_Applications', "Apps",
                line_color="#198754", fill_color="rgba(25, 135, 84, 0.1)"
            )

            # 3. Views (Cyan)
            fig_views = create_clean_line_chart(
                time_df, 'Date', 'Total_Views', "Views",
                line_color="#0dcaf0", fill_color="rgba(13, 202, 240, 0.1)"
            )
        else:
            fig_jobs, fig_apps, fig_views = empty_fig, empty_fig, empty_fig

        return (
            make_content("Total Jobs", f"{total_jobs:,}", "Posted Jobs"),
            make_content("Total Apps", f"{total_apps:,}", "Applications"),
            make_content("Total Views", f"{total_views:,}", "Job Views"),
            make_content("Avg Views/Job", f"{avg_views:,}", "Per Posting"),
            make_content("Avg Apps/Job", f"{avg_apps:,}", "Per Posting"),
            make_content("Conversion", conversion_str, "Apps / Views"),
            fig_jobs,
            fig_apps,
            fig_views
        )