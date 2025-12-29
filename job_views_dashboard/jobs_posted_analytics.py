import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import calendar  # Used to get Month names easily

# --- 1. STYLING & HELPER FUNCTIONS ---

glass_style = {
    'background': 'rgba(255, 255, 255, 0.8)',
    'backdropFilter': 'blur(12px)',
    'border': '1px solid rgba(255, 255, 255, 0.9)',
    'boxShadow': '0 8px 32px 0 rgba(31, 38, 135, 0.07)',
    'borderRadius': '15px',
    'marginBottom': '25px'
}


def create_detail_card(title, value, subtext, color, val_id=None):
    """
    Creates a detailed KPI card.
    """
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-uppercase text-white-100",
                    style={'fontSize': '0.8rem', 'fontWeight': 'bold'}),
            html.H3(value, id=val_id if val_id else "", className="text-white",
                    style={'fontWeight': 'bold', 'margin': '5px 0', 'fontSize': '1.8rem'}),
            html.Small(subtext, className="text-white-90", style={'fontSize': '0.75rem'})
        ]),
        color=color,
        inverse=True,
        className="kpi-card shadow-sm h-100",
        style={'borderRadius': '12px', 'border': 'none'}
    )


# --- 2. LAYOUT DEFINITION ---

layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col(html.H3("Jobs Posted Analytics", className="my-4", style={'fontWeight': '800', 'color': '#2c3e50'}),
                width=12)
    ]),

    # --- FILTERS (Now with 4 Columns) ---
    dbc.Row([
        # 1. Date Range
        dbc.Col([
            html.Label("Date Range", className="fw-bold small text-muted"),
            dcc.DatePickerRange(
                id='jpa-date-picker',
                display_format='YYYY-MM-DD',
                clearable=True,
                style={'width': '100%', 'borderRadius': '8px'}
            )
        ], width=12, md=3),

        # 2. Month Filter (NEW)
        dbc.Col([
            html.Label("Filter by Month", className="fw-bold small text-muted"),
            dcc.Dropdown(
                id='jpa-month-dropdown',
                options=[{'label': calendar.month_name[i], 'value': i} for i in range(1, 13)],
                multi=True,
                placeholder="Select Months..."
            )
        ], width=12, md=3),

        # 3. Category
        dbc.Col([
            html.Label("Job Category", className="fw-bold small text-muted"),
            dcc.Dropdown(id='jpa-category-dropdown', multi=True, placeholder="All Categories")
        ], width=12, md=3),

        # 4. Company
        dbc.Col([
            html.Label("Company", className="fw-bold small text-muted"),
            dcc.Dropdown(id='jpa-company-dropdown', multi=True, placeholder="All Companies")
        ], width=12, md=3),

    ], className="p-4 mb-4 bg-white shadow-sm", style={'borderRadius': '15px', 'borderLeft': '5px solid #6610f2'}),

    # --- KPI GRID (Now includes Median) ---
    dbc.Row([
        # Row 1: General Stats
        dbc.Col(create_detail_card("Total Jobs", "0", "Selected Period", "dark", "card-total"), width=12, sm=6, lg=4,
                xl=2, className="mb-3"),
        dbc.Col(create_detail_card("Avg Jobs/Day", "0", "Daily Mean", "info", "card-avg-day"), width=12, sm=6, lg=4,
                xl=2, className="mb-3"),
        dbc.Col(create_detail_card("Median Jobs/Day", "0", "Daily Median", "info", "card-median-day"), width=12, sm=6,
                lg=4, xl=2, className="mb-3"),  # NEW
        dbc.Col(create_detail_card("Avg Jobs/Month", "0", "Monthly Mean", "primary", "card-avg-month"), width=12, sm=6,
                lg=4, xl=2, className="mb-3"),
        dbc.Col(create_detail_card("Conversion", "0%", "Apps/Views", "danger", "card-conv"), width=12, sm=6, lg=4, xl=2,
                className="mb-3"),

        # Row 2: Highs & Lows
        dbc.Col(create_detail_card("Highest Day", "-", "Count (Date)", "success", "card-high-day"), width=12, sm=6,
                lg=4, className="mb-3"),
        dbc.Col(create_detail_card("Lowest Day", "-", "Count (Date)", "warning", "card-low-day"), width=12, sm=6, lg=4,
                className="mb-3"),

        # Row 3: Top Lists
        dbc.Col(create_detail_card("Top 3 Days", "-", "Date: Count", "secondary", "card-top3-day"), width=12, md=6,
                className="mb-3"),
        dbc.Col(create_detail_card("Top 3 Months", "-", "Month: Count", "secondary", "card-top3-month"), width=12, md=6,
                className="mb-3"),
    ]),

    # --- GRAPHS ---
    dbc.Row([
        # Graph 1: Daily Trend
        dbc.Col(dbc.Card([
            dbc.CardHeader("1. Jobs Posted vs Time (Daily)", className="bg-transparent fw-bold border-0"),
            dbc.CardBody(dcc.Graph(id='jpa-daily-graph', style={'height': '350px'}, config={'displayModeBar': False}))
        ], style=glass_style), width=12),

        # Graph 2: Monthly Trend
        dbc.Col(dbc.Card([
            dbc.CardHeader("2. Jobs Posted vs Time (Monthly)", className="bg-transparent fw-bold border-0"),
            dbc.CardBody(dcc.Graph(id='jpa-monthly-graph', style={'height': '350px'}, config={'displayModeBar': False}))
        ], style=glass_style), width=12),
    ]),

    # --- DATA TABLE ---
    dbc.Row([
        dbc.Col([
            html.H5("Detailed Job Data", className="mb-3 text-muted fw-bold"),
            html.Div(id='jpa-table-container', className="styled-table-container")
        ], width=12)
    ], className="mb-5")

], fluid=True)


# --- 3. CALLBACKS ---

def register_callbacks(app):
    # 1. Populate Dropdowns
    @app.callback(
        [Output('jpa-category-dropdown', 'options'),
         Output('jpa-company-dropdown', 'options')],
        Input('global-data-store', 'data')
    )
    def update_filters(data):
        if not data: return [], []
        df = pd.DataFrame(data)
        cats = [{'label': c, 'value': c} for c in
                sorted(df['Job_Category'].dropna().unique().astype(str))] if 'Job_Category' in df.columns else []
        comps = [{'label': c, 'value': c} for c in
                 sorted(df['Company'].dropna().unique().astype(str))] if 'Company' in df.columns else []
        return cats, comps

    # 2. Update Dashboard
    @app.callback(
        [
            Output('card-total', 'children'),
            Output('card-avg-day', 'children'),
            Output('card-median-day', 'children'),  # NEW Output
            Output('card-avg-month', 'children'),
            Output('card-conv', 'children'),
            Output('card-high-day', 'children'),
            Output('card-low-day', 'children'),
            Output('card-top3-day', 'children'),
            Output('card-top3-month', 'children'),
            Output('jpa-daily-graph', 'figure'),
            Output('jpa-monthly-graph', 'figure'),
            Output('jpa-table-container', 'children')
        ],
        [
            Input('global-data-store', 'data'),
            Input('jpa-date-picker', 'start_date'),
            Input('jpa-date-picker', 'end_date'),
            Input('jpa-month-dropdown', 'value'),  # NEW Input
            Input('jpa-category-dropdown', 'value'),
            Input('jpa-company-dropdown', 'value')
        ]
    )
    def update_analytics(data, start_date, end_date, selected_months, cats, comps):
        empty_fig = px.line(title="No Data")
        # Return default values if no data
        if not data:
            return "0", "0", "0", "0", "0%", "-", "-", "-", "-", empty_fig, empty_fig, None

        df = pd.DataFrame(data)

        # --- PREPROCESSING ---
        if 'Created_At' in df.columns:
            df['Created_At'] = pd.to_datetime(df['Created_At'], errors='coerce')

        for col in ['Total_Applications', 'Total_Views']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # --- FILTERING ---
        # 1. DateRange
        if start_date:
            df = df[df['Created_At'].dt.date >= pd.to_datetime(start_date).date()]
        if end_date:
            df = df[df['Created_At'].dt.date <= pd.to_datetime(end_date).date()]

        # 2. Month Filter (NEW)
        if selected_months:
            df = df[df['Created_At'].dt.month.isin(selected_months)]

        # 3. Category & Company
        if cats:
            df = df[df['Job_Category'].isin(cats)]
        if comps:
            df = df[df['Company'].isin(comps)]

        if df.empty:
            return "0", "0", "0", "0", "0%", "-", "-", "-", "-", empty_fig, empty_fig, None

        # --- KPI CALCULATIONS ---

        # 1. Total
        total_jobs = len(df)

        # 2. Daily Aggregations
        daily_counts = df.groupby(df['Created_At'].dt.date).size()

        # Averages & Median
        avg_day = round(daily_counts.mean(), 1)
        median_day = round(daily_counts.median(), 1)  # NEW Calculation

        # Highest Day with Date
        high_val = daily_counts.max()
        high_date = daily_counts.idxmax().strftime('%b %d')
        high_str = f"{high_val} ({high_date})"

        # Lowest Day with Date
        low_val = daily_counts.min()
        low_date = daily_counts.idxmin().strftime('%b %d')
        low_str = f"{low_val} ({low_date})"

        # Top 3 Days (Mode) with Counts
        # Format: "Oct 25: 150, Nov 01: 140"
        top3_days = daily_counts.nlargest(3)
        top3_days_str = ", ".join([f"{d.strftime('%b %d')}: {c}" for d, c in top3_days.items()])

        # 3. Monthly Aggregations
        df['Month_Year'] = df['Created_At'].dt.to_period('M')
        monthly_counts = df.groupby('Month_Year').size()
        avg_month = round(monthly_counts.mean(), 1)

        # Top 3 Months with Counts
        top3_months = monthly_counts.nlargest(3)
        top3_months_str = ", ".join([f"{str(m)}: {c}" for m, c in top3_months.items()])

        # 4. Conversion
        tot_apps = df['Total_Applications'].sum()
        tot_views = df['Total_Views'].sum()
        conv_rate = (tot_apps / tot_views * 100) if tot_views > 0 else 0

        # --- GRAPHS ---

        # Daily Graph
        daily_df = daily_counts.reset_index(name='Count')
        fig_daily = px.area(daily_df, x='Created_At', y='Count', markers=True, template="plotly_white")
        fig_daily.update_traces(line_color='#6610f2', line_shape='spline', fill='tozeroy')
        fig_daily.update_layout(margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)')

        # Monthly Graph
        monthly_df = monthly_counts.reset_index(name='Count')
        monthly_df['Month_Year'] = monthly_df['Month_Year'].astype(str)
        fig_monthly = px.bar(monthly_df, x='Month_Year', y='Count', template="plotly_white")
        fig_monthly.update_traces(marker_color='#fd7e14')
        fig_monthly.update_layout(margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)')

        # --- TABLE ---
        display_cols = ['Job_Title', 'Company', 'Job_Category', 'Created_At', 'Total_Views', 'Total_Applications']
        final_cols = [c for c in display_cols if c in df.columns]

        table = dash_table.DataTable(
            data=df[final_cols].sort_values('Created_At', ascending=False).head(50).to_dict('records'),
            columns=[{'name': i.replace('_', ' '), 'id': i} for i in final_cols],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'Segoe UI'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ]
        )

        return (
            f"{total_jobs:,}",
            f"{avg_day}",
            f"{median_day}",  # Median Output
            f"{avg_month}",
            f"{conv_rate:.2f}%",
            high_str,  # High with Date
            low_str,  # Low with Date
            top3_days_str,  # Top 3 Days with Counts
            top3_months_str,  # Top 3 Months with Counts
            fig_daily,
            fig_monthly,
            table
        )